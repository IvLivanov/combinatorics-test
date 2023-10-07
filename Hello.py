# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
import copy
import datetime
from datetime import timedelta
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

#Hiding the sidebar:
st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

def run():
   #Classes:
   total_spaces_small_tight = 45
   total_spaces_small_relax = 35
   total_spaces_median_tight = 35
   total_spaces_median_relax = 30
   k_groups = ['Jun inf', 'Jun sen', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth']
   st.session_state.show_dict = {'Jun inf': 'Space Shapes', 'Jun sen': 'Space Shapes', 'First': 'Polaris', 'Second': 'Polaris', 'Third': 'Roller Coaster', 'Fourth': 'Roller Coaster', 'Fifth': 'Space Quiz', 'Sixth': 'Space Quiz'}
   st.session_state.show_length = {'Space Shapes' : 20, 'Polaris': 20, 'Roller Coaster': 25, 'Space Quiz': 30}
   # Default schedule:
   if "times" not in st.session_state:
    st.session_state.times = [datetime.time(9, 30), datetime.time(11, 00), datetime.time(11, 10), datetime.time(14, 00)]


  #Dict for storing lists of pupils:
   if "table_dict" not in st.session_state:
    table_dict = dict((k_group, {'classes' : []}) for k_group in k_groups)
    st.session_state.table_dict = table_dict 
   else:
     table_dict = st.session_state.table_dict
   
  #Dict of storing text inputs to clear:
   if "clear_dict" not in st.session_state:
    clear_dict = dict((k_group, False) for k_group in k_groups)
    st.session_state.clear_dict = clear_dict
   else:
    for k_group in k_groups:
     if st.session_state.clear_dict[k_group]:
      st.write(k_group + 'cleared')
      st.session_state[k_group] = ''
      st.session_state.clear_dict[k_group] = False
   #Markup:
   col1, col2 = st.columns(2);
   with col1:
      st.header("number of pupils")
      for num, k_group in enumerate(k_groups):
        #Widgets magic
        st.subheader(k_group)
        class_input = st.number_input('input number of pupils', key = k_group + '_inpt', format = '%i', step = 1)
        table_dict[k_group]['num'] = class_input
        if st.button("add class", key = k_group + '_button') and class_input > 0:
          table_dict[k_group]['classes'].append(table_dict[k_group]['num'])
        if st.button("remove class", key = k_group + 'rm_button') and len(table_dict[k_group]['classes']) > 0:
          table_dict[k_group]['classes'].pop()
        for clas in table_dict[k_group]['classes']:
          st.write(clas)
        st.header(' ')
        st.header(' ')
    
    #Time management
   st.header('schedule') 
   t = st.time_input('add time here', value = datetime.time(9,00), step = 600)
   if st.button("add time") and t not in st.session_state.times:
    st.session_state.times.append(t)
    st.session_state.times.sort()
   if st.button("remove time") and len(st.session_state.times) > 0:
    st.session_state.times.pop()
   st.subheader('start')
   for n, time in enumerate(st.session_state.times):
    st.write(time)
    if n%2 == 0 and n < len(st.session_state.times) - 1:
      st.write('available time')
    elif n%2 == 1 and n < len(st.session_state.times) - 2:
      st.write('break')
   st.subheader('finish') 
   st.session_state.available_schedule = []
   for day in range(1, 6):
    for num in range(0, len(st.session_state.times)//2):
      tstart = datetime.datetime(2023, 10, day, st.session_state.times[num*2].hour,st.session_state.times[num*2].minute, st.session_state.times[num*2].second)
      tend =  datetime.datetime(2023, 10, day, st.session_state.times[num*2 + 1].hour, st.session_state.times[num*2 + 1].minute, st.session_state.times[num*2 + 1].second)
      st.session_state.available_schedule.append((tstart, tend));
   st.session_state.table_dict = table_dict
   st.session_state.table_dict_cur = copy.deepcopy(table_dict)


   with col2:
     st.header('results')
     tight = st.toggle('tight')
     if tight:
       total_spaces_small = total_spaces_small_tight
       total_spaces_median = total_spaces_median_tight
     else:
        total_spaces_small = total_spaces_small_relax
        total_spaces_median = total_spaces_median_relax
     st.session_state.space_dict = {'Jun inf' : total_spaces_small, 'Jun sen':total_spaces_small, 'First':total_spaces_small, 'Second':total_spaces_small, 'Third':total_spaces_small, 'Fourth':total_spaces_median, 'Fifth':total_spaces_median, 'Sixth':total_spaces_median}
     st.write("total spaces for small children: ", total_spaces_small)
     st.write("total spaces for median children: ", total_spaces_median)
     data = pack_children(k_groups, total_spaces_small, total_spaces_median)
   
#This is a master function in packing pupils into available schedule:
#It checks current schedule for existing show, where each class can be inserted and if 
#impossible to insert - creates a new show
def pack_children(k_groups, tot_spaces_small, tot_spaces_med):
  df = pd.DataFrame(columns = ['time_start', 'time_end', 'class', 'show'])
  st.session_state.current_schedule = []
  count = 0
  for group in k_groups:
   while  len(st.session_state.table_dict_cur[group]['classes']) > 0 and count < 10:
     if not insert_children(group, st.session_state.show_dict[group], st.session_state.space_dict[group]):
       create_show(df, st.session_state.show_dict[group], 20)
  st.table(st.session_state.current_schedule)
  download_
  data = pd.DataFrame(st.session_state.current_schedule)
  st.table(data)
  st.download_button('download table', data = pd.DataFrame.to_csv(data,index=False),)

def insert_children(group, show, total_spaces):
  clas = st.session_state.table_dict_cur[group]['classes'][-1]
  for num, slot in enumerate(st.session_state.current_schedule):
      if slot['show'] == show and slot['pupils'] + clas <= total_spaces:
        st.session_state.current_schedule[num]['pupils'] = slot['pupils'] + clas
        st.session_state.current_schedule[num]['classes'] += str(len(st.session_state.table_dict_cur[group]['classes'])) + ' ' + group + '; '
        st.session_state.table_dict_cur[group]['classes'].pop()
        return True
  return False




def create_show(df, showname, showlength):
  for num, time in enumerate(st.session_state.available_schedule):
    tstart, tend = time
    if tstart + datetime.timedelta(minutes = showlength) < tend:
      showend = tstart + datetime.timedelta(minutes = showlength)
      st.session_state.current_schedule.append({'day':tstart.strftime("%d")[1], 'time':(tstart.strftime("%H:%M") + '-' + showend.strftime("%H:%M")), 'show': showname, 'classes': '', 'pupils': 0})
      st.session_state.available_schedule[num] = showend, tend
      break
    
def time_offset(timeval, mins_to_add):
    # Convert timeval to seconds since midnight
    total_seconds = timeval.hour * 3600 + timeval.minute * 60 + timeval.second
    
    # Add the specified number of minutes in seconds
    total_seconds += mins_to_add * 60
    
    # Calculate the new time
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return datetime.time(hours, minutes, seconds)





if __name__ == "__main__":
    run()
