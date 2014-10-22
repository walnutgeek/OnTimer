.. title:: OnTimer Utils 

OnTimer Utils 
=============

.. automodule:: ontimer.utils

  Date utils
  ----------
  
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
 
  .. autoclass:: Broadcast
     :members:
  
  .. autoclass:: NiceDict
     :members:
 
  .. automethod:: ontimer.utils.pass_thru_transformation
  .. autoclass:: Propagator(callback, transformation=pass_thru_transformation)
     :members:
 
 
 
  .. autoclass:: KeyGroupValue
     :members:
  
  Object identification mixins
  ----------------------------

  .. autoclass:: KeyEqMixin
     :members:
 
  .. autoclass:: KeyCmpMixin
     :members:
  
  
  