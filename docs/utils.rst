.. title:: Utils 

Utils 
=====

.. automodule:: ontimer.utils

  Date utils
  ----------
  
  .. autodata:: format_Y_m_d_H_M_S_n
  .. autodata:: format_Y_m_d_H_M_S
  .. autodata:: format_Ymd_HMS
  .. autodata:: format_YmdHMS
  .. autodata:: format_Y_m_d
  .. autodata:: format_Ymd
  .. autodata:: all_formats
  .. automethod:: ontimer.utils.toDateTime
  .. automethod:: ontimer.utils.utc_adjusted
  
  Collections utils
  -----------------
  
  .. automethod:: ontimer.utils.quict
  .. automethod:: ontimer.utils.broadcast
  .. automethod:: ontimer.utils.flatten_links
  .. automethod:: ontimer.utils.safe_append
 
  .. autoclass:: Broadcast
     :members:
     
  .. autoclass:: BroadcastList
     :members:
     :inherited-members: 
  
    
  .. autoclass:: ProtectedDict
     :members:

  .. autoclass:: NiceDict
     :members:

  .. autoclass:: ABDict
     :members:
 
  .. automethod:: ontimer.utils.pass_thru_transformation

  .. autoclass:: Propagator (callback=None, broadcast=BroadcastList(), transformation=pass_thru_transformation)
     :members:
 
  Enums
  -----
  
  .. automethod:: ontimer.utils.find_enum
  .. automethod:: ontimer.utils.gen_doc_for_enums
  .. automethod:: ontimer.utils.enum_to_map
  
  
  Object identification mixins
  ----------------------------

  .. autoclass:: KeyEqMixin
     :members:
 
  .. autoclass:: KeyCmpMixin
     :members:
  
  Miscellaneous
  -------------
   
  .. automethod:: ontimer.utils.platform_info
  
  