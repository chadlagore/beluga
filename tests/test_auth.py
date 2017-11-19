import ujson as json

from beluga import app
from tests.utils import mock_users

def test_bad_google_session():
    _, response = app.test_client.post('/sessions', json={
        'service': 'google',
        'token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc3ZDRlZDYyZWUyMWQxNTdlOGEyMzdiN2RiM2NiZDhmN2FhZmFiMmUifQ.eyJhenAiOiIxNDg1Njc5ODY0NzUtaGpramlobnFuNTQ2MDMyMzV1NHJoaWxoNTRvc2NsY2MuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIxNDg1Njc5ODY0NzUtaGpramlobnFuNTQ2MDMyMzV1NHJoaWxoNTRvc2NsY2MuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDcwNDAzMDcwNDU2NDUxODc4ODUiLCJlbWFpbCI6ImpvcmRhbjkzNjRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJNX1FLUXhQQzZxbEZxUVAtcEJpYnlnIiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwiaWF0IjoxNTA5OTMxNDA1LCJleHAiOjE1MDk5MzUwMDUsIm5hbWUiOiJKb3JkYW4gSmVmZnJpZXMiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tLy1ScG1DNnJNMXJWcy9BQUFBQUFBQUFBSS9BQUFBQUFBQUF5dy9IeVQtNFhvbWZLcy9zOTYtYy9waG90by5qcGciLCJnaXZlbl9uYW1lIjoiSm9yZGFuIiwiZmFtaWx5X25hbWUiOiJKZWZmcmllcyIsImxvY2FsZSI6ImVuIn0.CFGeOxoE_CVowIGsHpYstB7no4MIbdFzu9XRM74os0QVGo1NKetXzIt7PTUbGutZkJCScuxJcXKdhOZDJKQrPdBo_Szw26WaKo_fYD7riE6yYakkjl5Z9MIqPiki6aJX6ktXcu1fdb77rtcsRTQ1AymuNoX8AfKdSjyotCi1WSlUXOt6y59gI-KWG9OmbXUEbXp1n0VV5iUhPb9gSQVFFD98JC4A3qGUDz0d9VQosugL42sti4J-VINCNDuG-IFUJ5KHisyCLGCGGzcZPqXDROrOZfeCu58bgxeHsKbOOqG4SAXJQ5xg7TPMkCkaoNY20wEQSZA1GFV_i8fv_4gKYA'
    })

    # This should fail because the token has expired
    assert response.status == 403

@mock_users()
def test_good_bearer_token():
    _, response = app.test_client.get('/users/self', headers={
        # User ID 1, signed with secret base in test Dockerfile
        'Authorization': 'Bearer eyJ0eXBlIjogImJlYXJlciIsICJ2YWwiOiAxfS5kYUhSY2F4eXYtUTNkNmpZM2tmNXRfdEl1NEk='
    })

    # We should be told that this functionality is unimplemented
    assert response.status == 501

def test_bad_bearer_token():
    _, response = app.test_client.get('/users/self', headers={
        'Authorization': 'Bearer BAD_TEST_TOKEN'
    })

    # We should be told we aren't allowed
    assert response.status == 403