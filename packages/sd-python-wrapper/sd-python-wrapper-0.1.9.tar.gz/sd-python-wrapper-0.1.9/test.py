from serverdensity.wrapper import ApiClient
from serverdensity.wrapper import Device

token = '2dfae5bf81f65492a40569d39b29ffa3'
client = ApiClient(token)
# device = client.devices.create(data={'name': 'testdevice'})


device2 = Device(token, name='name2')
device2.list()

