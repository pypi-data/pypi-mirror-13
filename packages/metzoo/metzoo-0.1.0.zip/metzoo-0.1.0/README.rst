To use , simply do::

    >>> import metzoo
    >>> 
    >>> customer= metzoo.Customer("c58d6977-999b-4c91-a7d0-d6e5a615d38b")
    >>> agent= customer.create_agent("host.004")
    >>> 
    >>> agent= metzoo.Agent('ac9a8c4c-af5d-5463-50c3-e282dd4c5056')
    >>> agent.create_metric("random.3")
    >>> agent.send_data({"random.3": 134.22})
