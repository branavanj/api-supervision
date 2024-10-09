from pysnmp.hlapi import *
from sqlalchemy.orm import Session
from models.supervision_results_model import SupervisionResult
from models.server_model import Server
from datetime import datetime

# Fonction de supervision SNMP
def supervise_snmp(server: Server, db: Session):
    try:
        iterator = getCmd(SnmpEngine(),
                         CommunityData('public', mpModel=0),
                         UdpTransportTarget((server.ip_address, 161)),
                         ContextData(),
                         ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')))
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            status = "Down"
            response_data = str(errorIndication)
        elif errorStatus:
            status = "Down"
            response_data = f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1] if errorIndex else '?'}"
        else:
            status = "Up"
            response_data = ', '.join([f"{name.prettyPrint()} = {val.prettyPrint()}" for name, val in varBinds])
    except Exception as e:
        status = "Down"
        response_data = str(e)

    # Enregistrer le résultat de la supervision
    supervision_result = SupervisionResult(
        server_id=server.id,
        status=status,
        response_data=response_data,
        timestamp=datetime.now()
    )
    db.add(supervision_result)
    db.commit()
    db.refresh(supervision_result)
    return supervision_result
