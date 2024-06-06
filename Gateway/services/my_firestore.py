import firebase_admin
from firebase_admin import firestore, messaging, credentials

cred = credentials.Certificate("./firebase-credentials.json")
firebase_admin.initialize_app(cred)


class MyFirestore:
    def __init__(self, brokerName, brokerUsername, brokerPassword):
        self.brokerDocumentId = brokerName + "-" + brokerUsername + "-" + brokerPassword
        self.rootDoc = firestore.client().collection("brokers").document(self.brokerDocumentId)

    def putSchedule(self, docId, js):
        self.rootDoc.collection("schedule").document(docId).set(js)

    def putHistory(self, js):
        self.rootDoc.collection("history").document().set(js)

    def deleteSchedule(self, docId):
        self.rootDoc.collection("schedule").document(docId).delete()

    def updateSchedule(self, docId, js):
        self.rootDoc.collection("schedule").document(docId).update(js)

    def getSchedules(self):
        return self.rootDoc.collection("schedule").get()

    def getSchedule(self, docId):
        return self.rootDoc.collection("schedule").document(docId).get()

    def isScheduleExist(self, docId):
        doc = self.rootDoc.collection("schedule").document(docId).get()
        if doc.exists:
            return True
        else:
            return False

    def putHistorySchedule(self, docId, js):
        self.rootDoc.collection("historySchedule").document(docId).set(js)


def sendMessage(title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        topic="notify"
    )

    response = messaging.send(message)

    print('Successfully sent message:', response)


