ALARM_TYPE_DESCRIPTIONS = {
    0: "Video Loss Alarm",
    1: "Video Block Alarm",
    3: "Memory Abnormality Alarm",
    7: "Emergency Alarm",
    8: "Speeding Alarm",
    9: "Low Voltage Alarm",
    38: "Illegal Shutdown Alarm",
    105: "GPS Loss Alarm",
    6005: "Front Close Blind Spot Alarm",
    17000: "Fence Alarm",
    17001: "Entering-Area Alarm",
    17002: "Out-Of-Area Alarm",
    17003: "Entering-Line Alarm",
    17004: "Out-Of-Line Alarm",
    17005: "Line Deviation Alarm",
    17006: "Excessive Road Section Driving Time Alarm",
    17007: "Fence Speeding Alarm",
    17008: "Insufficient Road Section Driving Time Alarm",
    17009: "Enter&Leave Fence Alarm",
    170010: "Limit-Time Alarm",
    18000: "X-direction",
    18001: "Y-direction",
    18002: "Z-direction",
    18006: "Rapid Acceleration",
    18007: "Rapid Deceleration",
    18010: "Sharp Left Turn",
    18011: "Sharp Right Turn",
    18015: "Shock",
    40001: "IO1 Alarm",
    40002: "IO2 Alarm",
    40003: "IO3 Alarm",
    40004: "IO4 Alarm",
    40005: "IO5 Alarm",
    40006: "IO6 Alarm",
    40007: "IO7 Alarm",
    40008: "IO8 Alarm",
    56000: "Driver Fatigue",
    56001: "No Driver",
    56002: "Driver Making Phone Calls",
    56003: "Driver Smoking",
    56004: "Driver Distraction",
    56005: "Lane Departure",
    56006: "Front Collision",
    56007: "Speed Limit Sign Alarm",
    56009: "Tailgating",
    56010: "Yawning",
    56011: "Pedestrian Collision",
    56016: "Unfastened Seat Belt",
    56018: "Blind Spot Detection (right)",
    56023: "Blind Spot Detection (left)",
    56025: "Intersection Speed Limit Alarm",
    56031: "STOP Sign Alarm",
    56046: "Blind Spot Detection (rear)",
    210000: "Abnormal Driving Alarm",
    210001: "Unknown Driver Alarm",
}


ALARMS_GAUSS_MAPPING = {
    # Distracciones

    56002: ("Distraction", "PhoneUse"),  # Uso del celular
    56004: ("Distraction", "DistractedDriving"),  # Conducir distraído
    56003: ("Distraction", "Smoking"),  # Fumar
    0: ("Distraction", "VideoLossAlarm"),  # Pérdida de video
    1: ("Distraction", "VideoBlockAlarm"),  # Bloqueo de video

    # Somnolencia
    56000: ("Drowsiness", "Microsleep"),  # Microsueño/Somnolencia
    56010: ("Drowsiness", "LightDrowsiness"),  # Bostezos/Light Drowsiness
    # Otros microsueños no especificados
    6005: ("SensorFieldOfViewObstruction", "CoveredSensors"),
    # Obstrucción de sensores

    # Fallas de sensores
    105: ("SensorFieldOfViewObstruction", "DeviceDeviation"),
    # Desviación de dispositivo

    # Estado del equipo
    9: ("VehicleStatus", "LowVoltage"),  # Bajo voltaje
    7: ("Driving", "EmergencyAlarm"),  # Alarma de emergencia

    # Conducción
    8: ("MaxSpeed", "Speeding"),  # Exceso de velocidad
    17005: ("Driving", "OutOfLane"),  # Salida de pista
    18006: ("Driving", "AbruptAcceleration"),  # Aceleración brusca
    18007: ("Driving", "HardBraking"),  # Frenado brusco
    18010: ("Driving", "SharpLeftTurn"),  # Giro brusco a la izquierda
    18011: ("Driving", "SharpRightTurn"),  # Giro brusco a la derecha
    56016: ("Driving", "UnfastenedSeatBelt"),
    # Cinturón de seguridad desabrochado

    # Exceso de velocidad en geozonas
    17007: ("MaxGeoSpeed", "MoreSevereGeoSpeeding"),
    # Exceso severo en geozona
    17008: ("MaxGeoSpeed", "SevereGeoSpeeding"),  # Exceso en geozona
    17009: ("MaxGeoSpeed", "NightGeoSpeeding"),  # Exceso nocturno en geozona
    170010: ("MaxGeoSpeed", "MorningGeoSpeeding"),  # Exceso diurno en geozona

    # Incumplimientos de protocolo
    210000: ("UnfulfilledProtocol", "FormNotEntered"),
    # Formulario no ingresado
    210001: ("UnfulfilledProtocol", "FormWithWrongData"),
    # Formulario con datos erróneos

    # Alarmas generales
    56006: ("Driving", "FrontCollision"),  # Colisión frontal
    56009: ("Driving", "Tailgating"),  # Seguimiento muy cercano
    56018: ("Driving", "BlindSpotDetectionRight"),
    # Detección de punto ciego (derecha)
    56023: ("Driving", "BlindSpotDetectionLeft"),
    # Detección de punto ciego (izquierda)
    56046: ("Driving", "BlindSpotDetectionRear"),
    # Detección de punto ciego (trasera)
    17000: ("MaxSpeed", "FenceAlarm"),  # Alarma de cerca
    17003: ("MaxSpeed", "EnteringLineAlarm"),  # Alarma al entrar en línea
    17004: ("MaxSpeed", "OutOfLineAlarm"),  # Alarma al salir de línea
}
