Exmaple of use:

    >>> import metzoo

    >>> # create an agent
    >>> agent = metzoo.Agent(CUSTOMER_KEY, "agent.name")
    <Agent 'agent.name', key: 'xxx...'>

    >>> # or with an url
    >>> agent = metzoo.Agent(CUSTOMER_KEY, "agent.name", "https://api.metzoo.com")
    <Agent 'agent.name', key: 'xxx...'>

    >>> # configure the metrics to use (optional)
    >>> agent.configure({"metric1.name": "unit", "metric2.name": "unit"})
    {"status":"ok"}

    >>> # send data for given metrics
    >>> agent.send({"metric1.name": 134.22, "metric2.name": 8123})
    {"status":"ok"}

    >>> # update own agent configuration
    >>> agent.update()
    {"status":"ok"}
