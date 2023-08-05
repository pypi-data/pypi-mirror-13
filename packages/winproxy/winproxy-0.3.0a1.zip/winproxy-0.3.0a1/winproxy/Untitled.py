
# coding: utf-8

# In[1]:

import sys, os
sys.path.append(os.path.join(os.getcwd(), '..'))


# In[2]:

import winproxy


# In[3]:

p = winproxy.ProxySetting()


# In[14]:

p.server


# In[11]:

p.enable=True


# In[13]:

p.registry_read()


# In[ ]:



