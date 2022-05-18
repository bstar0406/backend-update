from datetime import datetime
from pac.pre_costing.rateware import available_tariffs, error_code_lookup
from pac.rrf.models import RateBase


class RateWareTariffLoader:
    def __init__(self):
        self.tariffs = []
        self.rate_bases = []

    def load_available_tariffs(self, debug=False):
        print('Begin Loading Tariffs')

        self.tariffs = available_tariffs()
        if debug:
            print(f'loaded {len(self.tariffs)} rates from RateWare')

        self.tariffs_by_rate_base_name = {(x['tariffName'], x['effectiveDate']): x for x in self.tariffs}

        if len(self.tariffs) > len(self.tariffs_by_rate_base_name):
            # Duplicate data
            tariff_keys = [(x['tariffName'], x['effectiveDate']) for x in self.tariffs]
            dupes = [x for x in tariff_keys if tariff_keys.count(x) > 1]
            print(f'RateWare returned duplicate (TariffName, EffectiveDate) keys - Only one will be used: {dupes}')

        print('Done Loading Tariffs')

    def load_db_base_rates(self, debug=False):
        print('Begin Loading DB Base Rates')

        self.rate_bases = list(RateBase.objects.filter(is_active=True))
        if debug:
            print(f'loaded {len(self.rate_bases)} from database')

        self.rate_base_by_rate_base_name = {
            (x.rate_base_name, x.effective_date.strftime("%Y%m%d")): x for x in self.rate_bases}

        print('Done Loading DB Base Rates')

    def update_db_rate_bases(self, debug=False):
        print('Begin Update Base Rates')

        all_rates = sorted(
            set(
                list(self.tariffs_by_rate_base_name.keys()) + list(self.rate_base_by_rate_base_name.keys())
            )
        )

        for rate_effective_date in all_rates:
            if rate_effective_date not in self.rate_base_by_rate_base_name:
                # New Rate
                new_rate = self.tariffs_by_rate_base_name[rate_effective_date]

                new_rate_record = RateBase(
                    rate_base_name=new_rate['tariffName'],
                    description=new_rate['description'],
                    effective_date=datetime.strptime(new_rate['effectiveDate'], '%Y%m%d'),
                    product_number=new_rate['productNumber'],
                    release=new_rate['release'],
                )
                new_rate_record.is_modified = True
                self.rate_bases.append(new_rate_record)

                if debug:
                    print(f'Rate {rate_effective_date[0]} - {rate_effective_date[1]} adding to database')

            elif rate_effective_date not in self.tariffs_by_rate_base_name:
                # Deleted Rate
                deleted_rate = self.rate_base_by_rate_base_name[rate_effective_date]
                deleted_rate.is_active = False
                deleted_rate.is_inactive_viewable = False
                deleted_rate.is_modified = True

                if debug:
                    print(f'Rate {rate_effective_date[0]} - {rate_effective_date[1]} deactivating from database')
            else:
                # Check for changes
                rw_tariff = self.tariffs_by_rate_base_name[rate_effective_date]
                db_rate_base = self.rate_base_by_rate_base_name[rate_effective_date]

                if db_rate_base.description != rw_tariff['description']:
                    db_rate_base.description = rw_tariff['description']
                    db_rate_base.is_modified = True
                if db_rate_base.product_number != rw_tariff['productNumber']:
                    db_rate_base.product_number = rw_tariff['productNumber']
                    db_rate_base.is_modified = True

                if debug:
                    if hasattr(db_rate_base, 'is_modified') and db_rate_base.is_modified:
                        print(f'Rate {rate_effective_date[0]} - {rate_effective_date[1]} updated')

        print('Done Update Base Rates')

    def save_rate_bases(self, debug=True):
        print('Begin Save Data')

        # Only select modified RateBase records
        modified_rate_bases = []
        for rate_base in self.rate_bases:
            if hasattr(rate_base, 'is_modified') and rate_base.is_modified:
                modified_rate_bases.append(rate_base)

        print(f"Saving {len(modified_rate_bases)} modified RateBase records")

        for rate_base in modified_rate_bases:
            if debug:
                print(f'Saving {rate_base.rate_base_name} - {rate_base.effective_date}')
            rate_base.save()

        print('Done Save Data')
        pass
