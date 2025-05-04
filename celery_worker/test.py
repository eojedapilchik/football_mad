from match_event_service import MatchEventService

event_data = {
    "matchDetails": {
        "id": "ducrivfr5mdk38zys5ytlx638",
        "event": [
            {
                "id": 2809385025,
                "seqId": 1153,
                "eventId": 227,
                "typeId": 17,
                "periodId": 1,
                "timeMin": 27,
                "timeSec": 46,
                "contestantId": "8b523ujgl21tbc01me65q0aoh",
                "primaryKitColour": "#460C24",
                "playerId": "5jk0wq14a8emikh2vh53aw0ve",
                "playerName": "L. Delap",
                "outcome": 1,
                "x": 0,
                "y": 0,
                "timeStamp": "2025-05-03T14:28:59.482",
                "lastModified": "2025-05-03T14:29:02.688",
                "qualifier": [
                    {"id": 1510080383, "qualifierId": 35, "value": "NULL"},
                    {"id": 1510080384, "qualifierId": 31, "value": "NULL"},
                ],
            }
        ],
        "feedName": "matchEvent",
    }
}

goal_event_data = {
    "matchDetails": {
        "id": "ducrivfr5mdk38zys5ytlx638",
        "event": [
            {
                "id": 2809397727,
                "seqId": 1429,
                "eventId": 304,
                "typeId": 16,
                "periodId": 1,
                "timeMin": 34,
                "timeSec": 29,
                "contestantId": "ehd2iemqmschhj2ec0vayztzz",
                "primaryKitColour": "#0000CC",
                "secondaryKitColour": "#FFFFFF",
                "playerId": "7qgt7sht6py670pt6t4wjhqay",
                "playerName": "D. McNeil",
                "outcome": 1,
                "x": 75.5,
                "y": 31.4,
                "timeStamp": "2025-05-03T14:35:42.154",
                "lastModified": "2025-05-03T14:37:15.076",
                "qualifier": [
                    {"id": 1510149359, "qualifierId": 327, "value": "2"},
                    {"id": 1510149364, "qualifierId": 230, "value": "98.1"},
                    {"id": 1510149360, "qualifierId": 55, "value": "303"},
                    {"id": 1510149361, "qualifierId": 322, "value": "0.0291"},
                    {"id": 1510149367, "qualifierId": 326, "value": "1"},
                    {
                        "id": 1510149374,
                        "qualifierId": 374,
                        "value": "2025-05-03 15:35:40.434",
                    },
                    {"id": 1510149368, "qualifierId": 102, "value": "51.1"},
                    {"id": 1510149372, "qualifierId": 22, "value": "NULL"},
                    {"id": 1510149366, "qualifierId": 122, "value": "NULL"},
                    {"id": 1510149373, "qualifierId": 103, "value": "11.4"},
                    {"id": 1510149370, "qualifierId": 375, "value": "34:27.307"},
                    {"id": 1510149377, "qualifierId": 321, "value": "0.0251"},
                    {"id": 1510149375, "qualifierId": 18, "value": "NULL"},
                    {"id": 1510149369, "qualifierId": 29, "value": "NULL"},
                    {"id": 1510149371, "qualifierId": 215, "value": "NULL"},
                    {"id": 1510149362, "qualifierId": 56, "value": "Center"},
                    {"id": 1510149365, "qualifierId": 72, "value": "NULL"},
                    {"id": 1510149363, "qualifierId": 231, "value": "47.7"},
                    {"id": 1510149376, "qualifierId": 78, "value": "NULL"},
                ],
            }
        ],
        "feedName": "matchEvent",
    }
}

# Use a dummy sheet ID if testing without Google Sheets
service = MatchEventService("1ogMvKidrN86cMfYe7lii0mEqZ8AWojQ-Fwmm-MBYiQs")
response = service.process_event(goal_event_data)
print(response)
