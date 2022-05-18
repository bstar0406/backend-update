import io
import json
import logging
logging.getLogger().setLevel(logging.INFO)
import pyodbc
from rest_framework import status, views
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from pac.pre_costing.schemas import (CurrencyExchangeEditSchema)
from jsonschema import validate

class CurrencyExchangeDashboardView(views.APIView):
    # GET Queries
    GET_CURRENCY_EXCHANGE_HISTORY_LIST = """
        SELECT
            ceh.CADtoUSD 'cad_to_usd',
            ceh.USDtoCAD 'usd_to_cad',
            ceh.CurrencyExchangeID 'currency_exchange_id',
            ceh.IsActive 'is_active',
            ceh.IsLatestVersion 'is_latest_version',
            ceh.UpdatedOn 'updated_on',
            ceh.VersionNum 'version_num'
        FROM CurrencyExchange_History ceh
        WHERE ceh.IsActive = 1
        ORDER BY ceh.IsLatestVersion DESC, ceh.UpdatedOn DESC
    """

    # PUT Queries
    UPDATE_CE_BY_ID = """
        UPDATE CurrencyExchange SET
            CADtoUSD = {cadToUsd},
            USDtoCAD = {usdToCad}
        WHERE CurrencyExchangeID = {ceId}
    """

    UPDATE_CE_HIST_LATEST_VER = """
        UPDATE CurrencyExchange_History SET 
            IsLatestVersion = 0,
            UpdatedBy = '{userName}', 
            UpdatedOn = CURRENT_TIMESTAMP
        WHERE CurrencyExchangeID = {ceId} AND IsLatestVersion = 1
    """

    INSERT_CE_HISTORY = """
        INSERT INTO CurrencyExchange_History (
            VersionNum, IsActive, IsInactiveViewable, IsLatestVersion, Comments,
            CADtoUSD, USDtoCAD, CurrencyExchangeID, UpdatedBy, UpdatedOn
        ) SELECT
            (ISNULL(MAX(VersionNum),0) + 1), 1, 1, 1, '',
            {cadToUsd}, 
            {usdToCad},
            {ceId},
            '{userName}',
            CURRENT_TIMESTAMP
        FROM CurrencyExchange_History 
        WHERE CurrencyExchangeID = {ceId}
    """

    def get(self, request, *args, **kwargs):
        data = []
        # get connection.
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        # get the requested list of history.
        cursor.execute(self.GET_CURRENCY_EXCHANGE_HISTORY_LIST)
        raw_data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        for row in raw_data:
            data.append(dict(zip(columns, row)))
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # Connection
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        # get userName from the session
        userName = self.request.user.user_name
        # validate request body
        try:
            validate(instance=request.data[0], schema=CurrencyExchangeEditSchema)
        except Exception as e:
            # validation error
            return Response({
                'errorMessage': f"Body failed validation: {e}",
                'request': request.data
            }, status=status.HTTP_400_BAD_REQUEST)
        requestObj = request.data[0]
        # Params for the query.
        cadToUsd = requestObj.get('cad_to_usd')
        usdToCad = requestObj.get('usd_to_cad')
        currencyExchangeId = requestObj.get('currency_exchange_id')

        try:
            # Execute the update and provide the params.
            cursor.execute(self.UPDATE_CE_BY_ID.format(
                cadToUsd = cadToUsd,
                usdToCad = usdToCad,
                ceId = currencyExchangeId
            ))
            # Update previous latest version to no longer be latest.
            cursor.execute(self.UPDATE_CE_HIST_LATEST_VER.format(
                userName = userName,
                ceId = currencyExchangeId
            ))
            # Execute insert for new history record. 
            cursor.execute(self.INSERT_CE_HISTORY.format(
                cadToUsd = cadToUsd,
                usdToCad = usdToCad,
                ceId = currencyExchangeId,
                userName = userName
            ))
            cnxn.commit()
        except pyodbc.Error as ex:
            sqlstate = ex.args[1]
            return Response({
                'errorMessage': f"SQL Error: {sqlstate}",
                'request': requestObj
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "request": requestObj
        }, status=status.HTTP_200_OK)
