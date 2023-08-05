import metzoo

metzoo.API("http://staging-metzoo01.dev.edrans.net:8081")

customer= metzoo.Customer("c58d6977-999b-4c91-a7d0-d6e5a615d38b", debug=True)
agent= customer.create_agent("host.006")

agent= metzoo.Agent('ac9a8c4c-af5d-5463-50c3-e282dd4c5056', debug=True)
agent.create_metric("random.1")
agent.send_data({"random.3": 134.22})
