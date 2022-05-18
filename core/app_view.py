import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import buildFilterSchema, BulkInsertSchema, BulkUpdateSchema, buildInsertSchema, buildUpdateSchema
from jsonschema import validate


class AppView(views.APIView):
    # if multiple actions are to be performed in a transaction, set a class-wide connection object here
    #Otherwise, the transaction is presumed to be just for this one class and will commit when it completes the operation
    conn = None
    schema = None
    user_name = None

    PRIMARY_TABLE = 'dbo.Request'
    PRIMARY_KEY = 'id'
    AUDIT_COLUMNS = [] # an array of strings representing which columns should be copied into the History table
    AUDIT_VALUES = [] # an array of values to copy from the source table into the history table. This is an override of AUDIT_COLUMNS
    GET_ALL_QUERY = """SELECT * FROM {self.PRIMARY_TABLE} ORDER BY {self.PRIMARY_KEY}"""
    GET_SINGLE_QUERY = """SELECT * FROM {self.PRIMARY_TABLE} ORDER BY {self.PRIMARY_KEY} OFFSET 0 ROWS FETCH FIRST 1 ROWS ONLY"""
    GET_FILTERED_QUERY = """{opening_clause} {user_id} {page_clause} {sort_clause} {where_clauses} {closing_clause} """ # filtered query string should have these elements
    COLUMN_MAPPING = {} # put mapping for sorting and filtering in here
    OPENING_CLAUSE = " "
    CLOSING_CLAUSE = " "

    UPDATE_FIELDS = [] # an array of field names to use when update the record
    INSERT_FIELDS = [] # an array of field names to use when inserting the record

    def prepare_get(self, kwargs): # function to call in preparation for running the default GET behavior
        null_op = None

    def prepare_filter(self, data, kwargs): # optional function to prepare the class or data before filtering
        return data

    def after_filter(self, data, kwargs): # if additional work is required after the main query, it can be added here
        return data

    def prepare_bulk_update(self, data, kwargs): # optional function to prepare the class or data before bulk_update
        return data

    def prepare_bulk_insert(self, data, kwargs): # optional function to prepare the class or data before bulk_insert
        return data

    def after_bulk_insert(self, new_ids): # after bulk_insert, process the new primary_key_ids and handle any other post-ops
        if self.conn is not None and new_ids is not None and len(new_ids) > 0:
            self.conn.commit() # default behavior is to commit all changes if there were no errors

    def after_update(self, data, args, kwargs):
        if self.conn is not None:
            self.conn.commit() # default behavior is to commit all changes if there were no errors

    def fail_validation(self, data, schema):
        try:
            validate(instance=data, schema=schema)
        except Exception as e:
            # validation error returned here
             return Response({
                      'rows': [],
                      'count': 0,
                      'errorMessage': f"Body failed validation: {e}",
                      'request': data
                   }, status=status.HTTP_400_BAD_REQUEST)
        return False

    def process_sql_to_json(self, cursor, query, *args):
        cursor.execute(query)
        raw_data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data_rows = []
        for row in raw_data:
            data_rows.append(dict(zip(columns, row)))
        return data_rows

    def get(self, request, *args, **kwargs):
        primary_key_id = kwargs.get(self.PRIMARY_KEY)
        if primary_key_id is not None and primary_key_id > 0:
            return self.get_single(request, args, kwargs)
        else:
            return self.get_all(request, args, kwargs)


    def get_single(self, request, args, kwargs):
        try:
            self.prepare_get(kwargs)
            cnxn = pyodbc_connection()
            cursor = cnxn.cursor()
            query = self.GET_SINGLE_QUERY
            return Response(self.process_sql_to_json(cursor, query), status=status.HTTP_200_OK)
        except:
            return Response({
                'rows': [],
                'count': 0,
                'errorMessage': f"A record could not be found",
                'request': {}
                }, status=status.HTTP_400_BAD_REQUEST)

    def get_all(self, request, args, kwargs):
        try:
            self.prepare_get(kwargs)
            cnxn = pyodbc_connection()
            cursor = cnxn.cursor()
            query = self.GET_ALL_QUERY
            payload = self.process_sql_to_json(cursor, query)
            return Response(payload, status=status.HTTP_200_OK)
        except:
            return Response({
                'rows': [],
                'count': 0,
                'errorMessage': f"The request for records could not be completed",
                'request': {}
                }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        requestObj = request.data
        self.user_name = request.user.user_name # make audit logging info available
        if (requestObj is not None) and (requestObj.get('idFilters') is not None or requestObj.get('textFilters') is not None or requestObj.get('textIdFilters') is not None):
            return self.filter_results(requestObj, args, kwargs) # treat as a filtered request with filters in the body
        else:
            update_result = self.update_records(requestObj, args, kwargs) # treat as a bulk update request with one or more rows
            if update_result is None:
                return Response({"status": "Failure", "errorMessage": "Records could not be updated"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"status": "Success", "rowsUpdated": update_result}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        self.user_name = request.user.user_name # make audit logging info available
        new_ids = self.bulk_insert(request.data, kwargs)
        if new_ids is None:
            return Response({"status": "Failure", "error": "Records could not be inserted"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif isinstance(new_ids, str):
            return Response({
            'errorMessage': new_ids,
            'request': request.data
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Success", "ids": new_ids, "message": f"Created {len(new_ids)} new records"},
            status=status.HTTP_200_OK)

    def bulk_insert(self, requestObj, kwargs):
        # validate the request body matches the bulk update format
        bulk_check = self.fail_validation(requestObj, BulkInsertSchema)
        if bulk_check:
            return bulk_check
        # run any pre-processing specific to the executing class
        insert_rows = self.prepare_bulk_insert(requestObj, kwargs)
        if isinstance(insert_rows, str):
            return insert_rows # error message passed up
        elif insert_rows is None or len(insert_rows) == 0:
            return "No valid rows found for insertion"

        insert_schema = buildInsertSchema(self.INSERT_FIELDS)
        data_check = self.fail_validation(insert_rows, insert_schema)
        if data_check:
            return data_check
        conn = None
        try:
            new_ids = []
            if len(insert_rows) > 0:
                if self.conn is not None: # use an open connection from a current transaction
                    conn = self.conn
                else:
                    conn = pyodbc_connection() # open a new connection and a transaction

                for row in insert_rows:
                    # Not going to include a dupe-check on PKs. Inserts will fail in SQL causing an exception

                    # build the base INSERT statement
                    insert_str = f"INSERT INTO {self.PRIMARY_TABLE} "
                    insert_cols = ['IsActive', 'IsInactiveViewable'] # boilerplate values in all tables
                    insert_vals = ['1','1']
                    # build each assignment statement
                    for col in self.INSERT_FIELDS:
                        #type check the values, and wrap in quotations if they are a string value
                        colName = col.get('fieldName')
                        if isinstance(row[colName], str):
                            insert_cols.append(colName)
                            insert_vals.append(f"""'{row[colName]}'""")
                        else:
                            insert_cols.append(colName)
                            insert_vals.append(f"""{row[colName]}""")

                    # default columns
                    insert_str += f"""({','.join(insert_cols)}) VALUES ({','.join(insert_vals)})"""

                    just_column = self.PRIMARY_KEY.split('.') # get the column name but not the table alias
                    just_column = just_column[len(just_column) - 1]

                    # insert this record
                    cursor = conn.cursor()
                    cursor.execute(insert_str)
                    # get the new pk for audit update
                    cursor.execute("SELECT @@IDENTITY AS ID;")
                    new_id = cursor.fetchone()[0]
                    new_ids.append(new_id)
                    self.audit_change(conn, just_column, new_id, 'row created')
                # commit all changes if not part of a large transaction
                if self.conn is None:
                    conn.commit()
                else: # otherwise, signal the calling class to clean up and commit changes
                    self.after_bulk_insert(new_ids)

                return new_ids
        except Exception as e:
            if conn is not None:
                conn.rollback()
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return None


    # For server-side filtering, the executing class will use all these validation and verification steps
    # SQL injection should be prevented and only valid filter/sort columns should be used
    def filter_results(self, data, args, kwargs):
        requestObj = self.prepare_filter(data, kwargs)
        # get user_id from the session
        user_id = self.request.user.user_id
        if self.schema is None:
            return Response({
                  'rows': [], 'count': 0,
                  'errorMessage': f"This endpoint does not have a validation schema",
                  'request': requestObj
               }, status=status.HTTP_400_BAD_REQUEST)
        # validate request body
        filter_check = self.fail_validation(data, self.schema)
        if filter_check:
            return filter_check
        # retrieve pagination parameters for the query
        page_size = requestObj.get('pageSize')
        page_num = requestObj.get('pageNumber')

        # retrieve sorting parameters for the query
        sortField = requestObj.get('sort').get('sortField').strip()
        sortDirection = requestObj.get('sort').get('sortDirection')
        if sortField in self.COLUMN_MAPPING.keys():
            sortField = self.COLUMN_MAPPING[sortField]['sortColumn'] # get the SQL mapped value
            sortFlip1 = 1 if sortDirection == 'ASC' else 0
            sortFlip2 = 0 if sortDirection == 'ASC' else 1
            sortString = f"ORDER BY CASE WHEN {sortField} IS NULL THEN {sortFlip1} ELSE {sortFlip2} END {sortDirection}, {sortField} {sortDirection}, {self.PRIMARY_KEY} DESC"
        else: # fail out as this is not a valid column to sort or (or could revert to a default)
            return Response({
               'rows': [],
               'count': 0,
               'errorMessage': f"Not a recognized column to sort on {sortField}",
               'request': requestObj
            }, status=status.HTTP_400_BAD_REQUEST)

        # retrieve filtering parameters for the query
        idFilters = requestObj.get('idFilters')
        textFilters = requestObj.get('textFilters')
        textIdFilters = requestObj.get('textIdFilters')
        where_clauses = ''
        for currentFilter in idFilters:
            if currentFilter['fieldName'] in self.COLUMN_MAPPING.keys():
                filterText = self.COLUMN_MAPPING[currentFilter['fieldName']]['filter']
                flatIds = ','.join([str(i) for i in currentFilter['ids']])
                if len(flatIds) > 0:
                    where_clauses = where_clauses + filterText.format(flatIds) # [34] to 34
            else: # fail on invalid column filters
                return Response({
                   'rows': [],
                   'count': 0,
                   'errorMessage': f"Not a recognized column to filter on {currentFilter['fieldName']}",
                   'request': requestObj
                }, status=status.HTTP_400_BAD_REQUEST)
        for currentFilter in textFilters:
            if currentFilter['fieldName'] in self.COLUMN_MAPPING.keys():
                filterText = self.COLUMN_MAPPING[currentFilter['fieldName']]['filter']
                textValue = (currentFilter['filterText']).upper()
                if len(textValue) > 0:
                    where_clauses = where_clauses + filterText.format(textValue)
            else: # fail on invalid column filters
                return Response({
                    'rows': [],
                    'count': 0,
                    'errorMessage': f"Not a recognized column to filter on {currentFilter['fieldName']}",
                    'request': requestObj
                    }, status=status.HTTP_400_BAD_REQUEST)
        for currentFilter in textIdFilters:
            if currentFilter['fieldName'] in self.COLUMN_MAPPING.keys():
                filterText = self.COLUMN_MAPPING[currentFilter['fieldName']]['filter']
                flatIds = '","'.join(currentFilter['ids'])
                if len(flatIds) > 0: # ignore empty arrays
                    where_clauses = where_clauses + filterText.format(flatIds) # [34] to 34
            else: # fail on invalid column filters
                return Response({
                    'rows': [],
                    'count': 0,
                    'errorMessage': f"Not a recognized column to filter on {currentFilter['fieldName']}",
                    'request': requestObj
                    }, status=status.HTTP_400_BAD_REQUEST)

        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()

        # get the count of rows with the query
        countQuery = self.GET_FILTERED_QUERY.format(
            user_id=user_id,
            opening_clause = "SELECT count(1) FROM (",
            page_clause = " ",
            sort_clause = " ",
            where_clauses=where_clauses,
            closing_clause = " ) as counter")
        cursor.execute(countQuery)
        rawCount = cursor.fetchone()
        countValue = rawCount[0]

        # get the requested page of rows
        rowQuery = self.GET_FILTERED_QUERY.format(
            user_id=user_id,
            opening_clause = self.OPENING_CLAUSE,
            page_clause = f" OFFSET {(page_num - 1) * page_size} ROWS FETCH FIRST {page_size} ROWS ONLY",
            sort_clause = sortString,
            where_clauses=where_clauses,
            closing_clause = self.CLOSING_CLAUSE)
        payload = payload = self.process_sql_to_json(cursor, rowQuery)
        processed_payload = self.after_filter(payload, kwargs)
        return Response({
            "rows": processed_payload,
            "totalRows": countValue,
            "request": requestObj
        }, status=status.HTTP_200_OK)


    def update_records(self, data, args, kwargs):
        # validate the request body matches the bulk update format
        bulk_check = self.fail_validation(data, BulkUpdateSchema)
        if bulk_check:
            return bulk_check

        # run any pre-processing specific to the executing class
        data = self.prepare_bulk_update(data, kwargs)
        update_schema = buildUpdateSchema(self.UPDATE_FIELDS)
        data_check = self.fail_validation(data, update_schema)
        if data_check:
            return data_check
        conn = None
        try:
            update_rows = data.get('records')
            update_count = 0
            if len(update_rows) > 0:
                if self.conn is not None: # use an open connection from a current transaction
                    conn = self.conn
                else:
                    conn = pyodbc_connection() # open a new connection and a transaction

                for row in update_rows:
                    pk_id = row.get("id")
                    values = row.get('data')

                    # build the base UPDATE statement
                    update_str = f"UPDATE {self.PRIMARY_TABLE} SET "
                    # build each assignment statement
                    for col in self.UPDATE_FIELDS:
                        #type check the values, and wrap in quotations if they are a string value
                        colName = col.get('fieldName')
                        if isinstance(values[colName], str):
                            update_str += f""" {colName} = '{values[colName]}' ,"""
                        else:
                            update_str += f" {colName} = {values[colName]} ,"

                    update_str = update_str[:-1] # remove last comma
                    just_column = self.PRIMARY_KEY.split('.') # get the column name but not the table alias
                    just_column = just_column[len(just_column) - 1]
                    update_str += f" WHERE {just_column} = {pk_id}"
                    # insert this record
                    updated_count = conn.execute(update_str)
                    self.audit_change(conn, just_column, pk_id, 'row values updated')
                    update_count += 1
                # commit all changes if not part of a large transaction
                if self.conn is None:
                    conn.commit()
                else: # otherwise, signal the calling class to clean up and commit changes
                    self.after_update(data, args, kwargs)

            return update_count
        except Exception as e:
            if conn is not None:
                conn.rollback()
            logging.warning(f"{e}")
            return None

    def audit_change (self, conn, primary_column, pk_id, comment):
        # format the column strings
        audit_columns = ','.join(self.AUDIT_COLUMNS)
        audit_values = ''
        if len(self.AUDIT_VALUES) == 0:
            audit_values = ','.join(self.AUDIT_COLUMNS)
        else:
            audit_values = ','.join(self.AUDIT_VALUES)
        # create audit insert statements
        audit_statement = """
            DECLARE @LatestID bigint;
            DECLARE @LatestNum bigint;

            SELECT @LatestID = {table}VersionID
            FROM dbo.{table}_History WHERE {column} = {pk_id} and IsLatestVersion = 1;
            SELECT @LatestNum =ISNULL(
                (SELECT VersionNum FROM dbo.{table}_History WHERE {column} = {pk_id} and IsLatestVersion = 1) , 0);

            UPDATE dbo.{table}_History set IsLatestVersion = 0 WHERE {table}VersionID = @LatestID;
            INSERT INTO dbo.{table}_History
            (IsActive, IsInactiveViewable, {audit_columns} ,
                VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments)
            SELECT
                IsActive,
                IsInactiveViewable,
                {audit_values} ,
                (@LatestNum + 1) VersionNum,
                1 IsLatestVersion,
                GETDATE() UpdatedOn,
                '{user_name}' UpdatedBy,
                NULL BaseVersion,
                'Row updated' Comments
             FROM dbo.{table} where {column} = {pk_id};
             """
        table_name = self.PRIMARY_TABLE.split('dbo.')[1] if self.PRIMARY_TABLE.find('dbo.') > -1 else self.PRIMARY_TABLE
        audit_statement = audit_statement.format(table = table_name,
                                       column = primary_column,
                                       pk_id = pk_id,
                                       user_name = self.user_name,
                                       audit_columns = audit_columns,
                                       audit_values = audit_values)
        # update the history table, and let any errors pass up to the error handling of calling function
        conn.execute(audit_statement)
