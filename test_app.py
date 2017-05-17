import unittest
from app import app
import json

class TestNLPServices(unittest.TestCase):

   
  def test_authorize(self):
    self.test_app=app.test_client(self)
    data = {'appId': 1}
    headers = {'Content-Type' : 'application/json'}
    response=self.test_app.post('/authenticate',data=json.dumps(data), headers=headers)    
    self.assertEqual(response.status, "200 OK")

  def test_unauthorize(self):
    self.test_app=app.test_client(self)
    data = {'appId': 1000}
    headers = {'Content-Type' : 'application/json'}
    response=self.test_app.post('/authenticate',data=json.dumps(data), headers=headers)    
    self.assertEqual(response.status, '401 UNAUTHORIZED')    

  def test_sendMessage_tokenless(self):
    self.test_app=app.test_client(self)
    data = {'message': 'i broke my mobile'}
    headers = {'Content-Type' : 'application/json'}
    response=self.test_app.post('/processMessage',data=json.dumps(data), headers=headers)
    self.assertEqual(response.status, '401 UNAUTHORIZED') 

  def test_sendMessage_invalidToken(self):
    self.test_app=app.test_client(self)
    key='invalidtoken'    
    data = {'message': 'i broke my mobile'}
    headers = {'Content-Type' : 'application/json','authorization':key}
    response=self.test_app.post('/processMessage',data=json.dumps(data), headers=headers)
    self.assertEqual(response.status, '401 UNAUTHORIZED') 
    

  # def test_sendMessage_validToken(self):
  #   self.test_app=app.test_client(self)
  #   data = {'appId': 1}
  #   headers = {'Content-Type' : 'application/json'}
  #   response=self.test_app.post('/authenticate',data=json.dumps(data), headers=headers)  
  #   key=json.loads(response.data.decode('utf-8'))['token']    
  #   data = {'message': 'i broke my mobile'}
  #   headers = {'Content-Type' : 'application/json','authorization':key}
  #   response=self.test_app.post('/processMessage',data=json.dumps(data), headers=headers)
  #   self.assertEqual(response.status, "200 OK")  

  def test_sendMessage_dataNotProvided(self):
    self.test_app=app.test_client(self)
    data = {'appId': 1}
    headers = {'Content-Type' : 'application/json'}
    response=self.test_app.post('/authenticate',data=json.dumps(data), headers=headers)  
    key=json.loads(response.data.decode('utf-8'))['token']     
    headers = {'Content-Type' : 'application/json','authorization':key}
    response=self.test_app.post('/processMessage', headers=headers)
    self.assertEqual(response.status, "200 OK")     
    self.assertEqual(json.loads(response.data.decode('utf-8'))['message'],"Data is not provided")  
    

if __name__ == '__main__':
    unittest.main()