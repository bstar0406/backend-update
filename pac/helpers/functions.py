import json
import re

from django.db import transaction
from django.db.models import Q
import time

from pac.models import TerminalHistory
from pac.rrf.models import FreightClassHistory
from pac.settings.settings import CPU_COUNT

from django_bulk_update.helper import bulk_update


def batches(objs):
    batch_size = int(len(objs) / CPU_COUNT) or 1
    for j in range(0, len(objs), batch_size):
        yield objs[j:j + batch_size]


@transaction.atomic
def delete_instance(instance):
    instance.is_active = False
    instance.is_inactive_viewable = False
    instance.save()


@transaction.atomic
def archive_instance(instance):
    instance.is_active = False
    instance.is_inactive_viewable = True
    instance.save()


@transaction.atomic
def unarchive_instance(instance):
    instance.is_active = True
    instance.is_inactive_viewable = True
    instance.save()


@transaction.atomic
def revert_instance(instance, history_instance, serializer):
    instance._base_version = history_instance.version_num

    fields = [field for field in type(instance)._meta.get_fields()
              if field.concrete]
    data_dict = {}

    for field in fields:
        if field.get_internal_type() in ["BigAutoField", "AutoField"]:
            continue
        if field.get_internal_type() in ["ForeignKey", "OneToOneField"]:
            data_dict[field.name] = getattr(getattr(getattr(
                history_instance, field.name + "_version", None), camel_to_snake(field.related_model.__name__), None),
                "pk", None)
        else:
            data_dict[field.name] = getattr(history_instance, field.name)

    serializer_instance = serializer(instance, data=data_dict)
    serializer_instance.is_valid(raise_exception=True)
    serializer_instance.save()

    return serializer_instance.data


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Called by create_instance_history_bulk(list[Objects], globals())
# Enure that calling globals has both class and history imported for all affected classes
@transaction.atomic
def update_instance_history_bulk(instances_all, globals, batch_size=0, update_fields=None):
    print('--Start update_instance_history_bulk--')
    if not len(instances_all):
        return

    if not batch_size:
        batch_size = len(instances_all)

    insatnces_chunks = [instances_all[i * batch_size: (i + 1) * batch_size]
                        for i in range((len(instances_all) + batch_size - 1) // batch_size)]

    for instances in insatnces_chunks:
        print(f'--Running batch of {len(instances)} records--')

        if len(set(type(x).__name__ for x in instances)) > 1:
            raise "create_instance_history_bulk - All instances must be of the same type"

        previous_history_instance_list = {}  # Value: Result
        base_history_instance_list = {}  # Value: (VersionNum, Result)
        related_history_instance_list = {}  # Value: {PK, Result}

        history_instances = []

        # Aggregate and prepare to query History and Base Hisotry records
        for instance in instances:
            instance_cls_name = type(instance).__name__
            instance_cls_name_snake = camel_to_snake(instance_cls_name)
            history_cls_name = instance_cls_name + "History"
            # history_instance = globals[history_cls_name]()
            previous_history_instance_list[instance.pk] = None

            base_version = getattr(instance, '_base_version', False)

            if base_version:
                base_history_instance_list[instance.pk] = (base_version, None)

        # Get History records bulk
        print('--Get History records bulk--')
        previous_history_instance_data = globals[history_cls_name].objects.filter(
            **{instance_cls_name_snake + '_id__in': previous_history_instance_list.keys()}, is_latest_version=True)
        for previous_history_instance in previous_history_instance_data:
            previous_history_instance_list[getattr(
                previous_history_instance, instance_cls_name_snake + '_id')] = previous_history_instance

        query = Q()
        for base_history_key in base_history_instance_list:
            version_num = base_history_instance_list[base_history_key][0]
            query.add(Q(**{instance_cls_name_snake + '_id__in': base_history_key}, version_num=version_num), Q.OR)

        if len(query):
            base_history_instance_data = globals[history_cls_name].objects.filter(query)
            for base_history_instance in base_history_instance_data:
                base_history_instance_list[getattr(previous_history_instance,
                                                   instance_cls_name_snake + '_id')][1] = base_history_instance

        # Foreign Key Prefetch Prep
        print('--Foreign Key Prefetch Prep--')
        for instance in instances:
            fields = [field for field in type(instance)._meta.get_fields() if field.concrete]
            for field in fields:
                if field.get_internal_type() in ["ForeignKey", "OneToOneField"]:
                    field_name_id = field.name + '_id'
                    field_name_value = getattr(instance, field_name_id)
                    if field_name_value:
                        related_cls = field.related_model
                        related_cls_name = related_cls.__name__
                        related_cls_name_pk_key = (related_cls_name + "History", related_cls._meta.pk.name)

                        if related_cls_name_pk_key not in related_history_instance_list:
                            related_history_instance_list[related_cls_name_pk_key] = {}
                        related_history_instance_list[related_cls_name_pk_key][field_name_value] = None

        # Foreign Key Prefetch
        print('--Foreign Key Prefetch--')
        for table_pk_key in related_history_instance_list:
            table_name = table_pk_key[0]
            table_pk_name = table_pk_key[1]
            id_list = list(related_history_instance_list[table_pk_key].keys())

            related_history_instances = globals[table_name].objects.filter(
                **{table_pk_name+'__in': id_list}, is_latest_version=True)

            for related_history_instance in related_history_instances:
                related_history_instance_list[table_pk_key][
                    getattr(related_history_instance, table_pk_name)] = related_history_instance

        print('--Field Mapping--')
        for instance in instances:
            history_instance = globals[history_cls_name]()
            base_version = getattr(instance, '_base_version', False)
            base_history_instance = base_history_instance_list[instance.pk][1] if base_version else None
            previous_history_instance = previous_history_instance_list[instance.pk]

            setattr(history_instance, instance_cls_name_snake, instance)

            fields = [field for field in type(instance)._meta.get_fields() if field.concrete]
            for field in fields:
                if field.name == instance_cls_name_snake or field.get_internal_type() in ["BigAutoField", "AutoField"]:
                    continue
                elif field.get_internal_type() in ["ForeignKey", "OneToOneField"]:
                    # field_name = field.name
                    field_name_id = field.name + '_id'
                    field_name_value = getattr(instance, field_name_id)
                    if not field_name_value:
                        setattr(history_instance, field_name_id, field_name_value)
                        continue

                    related_cls = field.related_model
                    related_cls_name = related_cls.__name__
                    related_cls_name_pk_key = (related_cls_name + "History", related_cls._meta.pk.name)

                    related_history_instance = related_history_instance_list[related_cls_name_pk_key][
                        getattr(instance, field_name_id)]
                    # related_history_instance = related_history_instance_list[related_cls_name_pk_key][field_name_id]
                    # related_history_instance = globals[related_cls_name + "History"].objects.filter(
                    #     **{related_cls._meta.pk.name: getattr(instance, field_name).pk}, is_latest_version=True).first()
                    if base_version:
                        related_history_instance = getattr(base_history_instance, field.name + "_version")
                    if related_history_instance:
                        setattr(history_instance, field.name + "_version", related_history_instance)
                elif field.get_internal_type() == "TextField" and instance_cls_name in ["LaneRoute", "DockRoute",
                                                                                        "TerminalCost", "LaneCost", "LegCost",
                                                                                        "BrokerContractCost", "RequestProfile"]:
                    json_dict = json.loads(getattr(instance, field.name))
                    new_json_dict = json_to_history(json_dict)
                    new_json = json.dumps(new_json_dict)
                    setattr(history_instance, field.name, new_json)
                else:
                    setattr(history_instance, field.name,
                            getattr(instance, field.name))

            history_instance.base_version = base_version if base_version else None

            if previous_history_instance:
                history_instance.version_num = previous_history_instance.version_num + 1

            history_instances.append(history_instance)

        print('--Bulk Update--')
        # instance.save()
        start_time = time.time()
        bulk_update(instances, batch_size=batch_size, update_fields=update_fields)
        print("--- Bulk Update completed in %s seconds ---" % (time.time() - start_time))

        print('--Create History Records--')
        # previous_history_instance.save() -> set is_latest_version = False
        globals[history_cls_name].objects.filter(
            **{instance_cls_name_snake + '_id__in': previous_history_instance_list.keys()},
            is_latest_version=True).update(
            is_latest_version=False)

        # history_instance.save() -> bulk_create new history records
        globals[history_cls_name].objects.bulk_create(history_instances)


def create_instance_history(sender, instance, globals):
    instance_cls_name = sender.__name__
    instance_cls_name_snake = camel_to_snake(instance_cls_name)
    history_cls_name = instance_cls_name + "History"
    history_instance = globals[history_cls_name]()
    previous_history_instance = globals[history_cls_name].objects.filter(
        **{instance_cls_name_snake: instance}, is_latest_version=True).first()
    base_history_instance = None

    setattr(history_instance, instance_cls_name_snake, instance)
    base_version = getattr(instance, '_base_version', False)

    if base_version:
        base_history_instance = globals[history_cls_name].objects.filter(
            **{instance_cls_name_snake: instance}, version_num=base_version).first()

    fields = [field for field in sender._meta.get_fields() if field.concrete]

    for field in fields:
        if field.name == instance_cls_name_snake or field.get_internal_type() in ["BigAutoField", "AutoField"]:
            continue
        elif field.get_internal_type() in ["ForeignKey", "OneToOneField"]:
            field_name = field.name
            if not getattr(instance, field_name):
                setattr(history_instance, field_name, getattr(instance, field_name))
                continue
            related_cls = field.related_model
            related_cls_name = related_cls.__name__
            related_history_instance = globals[related_cls_name + "History"].objects.filter(
                **{related_cls._meta.pk.name: getattr(instance, field_name).pk}, is_latest_version=True).first()
            if base_version:
                related_history_instance = getattr(base_history_instance, field_name + "_version")
            if related_history_instance:
                setattr(history_instance, field_name + "_version", related_history_instance)
        elif field.get_internal_type() == "TextField" and instance_cls_name in ["LaneRoute", "DockRoute",
                                                                                "TerminalCost", "LaneCost", "LegCost",
                                                                                "BrokerContractCost", "RequestProfile"]:
            json_dict = json.loads(getattr(instance, field.name))
            new_json_dict = json_to_history(json_dict)
            new_json = json.dumps(new_json_dict)
            setattr(history_instance, field.name, new_json)
        else:
            setattr(history_instance, field.name,
                    getattr(instance, field.name))

    if previous_history_instance:
        history_instance.version_num = previous_history_instance.version_num + 1
        previous_history_instance.is_latest_version = False
        previous_history_instance.save()

    history_instance.base_version = base_version if base_version else None

    history_instance.save()


MAPPING = {"LegOriginTerminalID": ("LegOriginTerminalVersionID", TerminalHistory, "terminal_id"),
           "LegDestinationTerminalID": ("LegDestinationTerminalVersionID", TerminalHistory, "terminal_id"),
           "FreightClassID": ("FreightClassVersionID", FreightClassHistory, "freight_class_id")}


def json_to_history(data):
    if isinstance(data, list):
        new = []
        for obj in data:
            new.append(json_to_history(obj))
        return new
    elif isinstance(data, dict):
        new = {}
        for k, v in data.items():
            if k in MAPPING:
                new[MAPPING[k][0]] = MAPPING[k][1].objects.filter(
                    **{MAPPING[k][2]: v}, is_latest_version=True).first().pk
            else:
                new[k] = json_to_history(v)
        return new
    else:
        return data
