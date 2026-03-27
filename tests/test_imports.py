def test_xander_import():
    import xander
    assert hasattr(xander, "HiveBroker")

def test_agent_session_import():
    from xander import AgentSession
    assert AgentSession is not None
