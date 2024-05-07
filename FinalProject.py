'''
Name: Caroline Johannes
CS230: Section 001
Data: 2017 MA Motor Vehicle Crashes

Description:
This program displays a four-page web-based python app. The Home page includes a header and a brief description. The second page,
Crashes Map by Severity, displays a map of Massachusetts, with all the crashes overlayed by location. I included a dropdown 
multiselect for the user to choose which type of crash severity to view. The third page, Hit and Run by Town and Date, displays a
bar chart showing the total hit and runs in each city/town, with a range slider bar, so that users can select which time frame to 
view. The fourth and final page, Distracted Driving by Speed Limit, displays instances of distracted driving by road speed limit, 
while providing the user with friendly advice to keep their eyes on the road!
'''
import subprocess
subprocess.call(["pip", "install", "matplotlib"])

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import numpy as np
import datetime


def introPage():
    '''
    @param: N/a
    @returns: N/a
    -This function creates an introductory page for my project. It includes the assignment, my name, class, and the semester.
    -I also included an image of a car crash at Dunkin Donuts to speak to the dataset and Massachusetts' affinity for Dunkin.
    -The image is from the Boston Globe: (https://www.bostonglobe.com/metro/2015/10/25/injured-after-car-crashes-into-dunkin-
    donuts-canton/O2Fvk7dkbxCXb29ZoJKwkO/story.html)
    ''' 
    #create a header with Times New Roman font, left-aligned, in the color
    st.markdown("<h1 style='text-align: left; color: darkblue; font-family: Times New Roman;'>An Overview of 2017 Motor Vehicle Crashes in Massachusetts</h1>", unsafe_allow_html=True)

    
    st.header("Caroline Johannes")
    st.subheader("CS230-1, Bentley University, Spring 2024")
    st.subheader("Professor Tamara Babaian")
    st.write("This interactive web-based Python application provides visualized data of 2017 MA motor vehicle crashes. This application qualifies the nature of collision incidents, with the potential to provide the user insight into a variety of safety factors. Data is provided from Mass DOT.")
    st.image("DunkinTime.jpeg")
    return 

def CleanedData(df):
    '''
    @param: data frame
    @returns: cleaned data frame
    -This function removes rows with NaN entries in each of the columns which I use for this project
    '''
    #remove rows with NaN in CITY_TOWN_NAME
    cleaneddf = df.dropna(subset = 'CITY_TOWN_NAME')
    
    #remove rows with NaN in CRASH_SEVERITY_DESCR
    cleaneddf = cleaneddf.dropna(subset = 'CRASH_SEVERITY_DESCR')
    
    #remove rows with NaN in LAT
    cleaneddf = cleaneddf.dropna(subset = 'LAT')
    
    #remove rows with NaN in LON
    cleaneddf = cleaneddf.dropna(subset = 'LON')
    
    #remove rows with NaN in CRASH_DATE_TEXT
    cleaneddf = cleaneddf.dropna(subset = 'CRASH_DATE_TEXT')
    
    #remove rows with NaN in HIT_RUN_DESCR
    cleaneddf = cleaneddf.dropna(subset = 'HIT_RUN_DESCR')
    
    #remove rows with NaN in SPEED_LIM
    cleaneddf = cleaneddf.dropna(subset = 'SPEED_LIM')
    
    #remove rows with NaN in DRVR_CNTRB_CIRC_CL
    cleaneddf = cleaneddf.dropna(subset = 'DRVR_CNTRB_CIRC_CL')
    
    return cleaneddf

def crashMap(df):
    '''
    @param: data frame
    @returns: N/a
    -This function utilizes pydeck and to display a detailed map of MA, with a scatterplot of the crash
    location, using latitude and longitude, and streamlit multiselect to take user input for the severity
    type they would like to see displayed.
    -For this function's code, I used map.py and widgets.py for guidance.
    '''
    #title
    st.markdown("<h1 style='color: darkblue; font-family: Times New Roman;'>Map of MA Motor Vehicle Crashes in 2017, by Crash Severity</h1>", unsafe_allow_html=True)

    #assign value to the crash severity description column
    allSeverities = df["CRASH_SEVERITY_DESCR"]
    
    #create a list displaying all severity options
    severity = ["All"]
    for sev in allSeverities:
        if sev not in severity:
            severity.append(sev)
            
    #apply this list to a multiselect box, with a default
    severity_option = st.multiselect("Select crash severity:", severity, default = 'All')
    
    #if the severity option chosen is not "All", reassign the df used to be just entries with the 
    #crash severity matching the option chosen
    if "All" not in severity_option:
        df = df[df.CRASH_SEVERITY_DESCR.isin(severity_option)]
    
    #specify view state of the map
    view_state = pdk.ViewState(
        latitude=df["LAT"].mean(),
        longitude=df["LON"].mean(),
        zoom=6.75,
        pitch=0)    
    

    #create a scatterplot layer 
    layer1 = pdk.Layer('ScatterplotLayer',
                    data = df,
                    get_position='[LON, LAT]',
                    get_radius=500,
                    get_color=[0,0,255],   # big red circle
                    pickable=True
                      )
    #create a tooltip
    tool_tip = {"html": "Crash Date:<br/> <b>{CRASH_DATE_TEXT}</b><br/>City/Town Name: <br/><b>{CITY_TOWN_NAME}</b>",
        "style": { "backgroundColor": "crimson",
                            "color": "white"}
            }
    #create a map visualization in pydeck
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state,
        layers=[layer1],
        tooltip= tool_tip
    )

    st.pydeck_chart(map)
    



def hitAndRunbar(df, color = ['gray', 'cyan', 'blue','darkblue']):
    '''
    @param: data frame, color with default ['gray', 'cyan', 'blue','darkblue']
    @returns: N/a
    -This function creates a barchart of frequencies of town hit-and-runs, with a streamlit slider for
    date input
    -I used the code from PlottingWithinStreamlit3.py as a guide for creating the code for the bar chart
    and utilized widgets.py for creating the slider.
    ''' 
    #title
    st.markdown("<h1 style='color: darkblue; font-family: Times New Roman;'>Bar Chart of Hit-and-Runs By Town and Date</h1>", unsafe_allow_html=True)

    #initializing date slider info:
    st.write("What date(s) would you like to view? ")
    
    #create new column with the CRASH_DATE_TEXT as a datetime
    df["CRASH_DATE"] = pd.to_datetime(df["CRASH_DATE_TEXT"])
    
    #create the overall min and max range for the range slider: from beginning of 2017 to the end
    min_max_range = (datetime.datetime(2017,1,1),datetime.datetime(2017,12,31))
    
    #create date slider - tuple
    dtlowhigh = st.slider('Select a date range',
                  min_value = min_max_range[0],
                  max_value = min_max_range[1],
                  value = min_max_range
                )
    
    #specify start and end dates of the user input from the range slider
    start_date = dtlowhigh[0]
    end_date = dtlowhigh[1]
    
    #use the user input from the slider to filter the data based on the date range
    userinp = (df['CRASH_DATE'] >= start_date) & (df['CRASH_DATE'] <= end_date)
    df = df.loc[userinp]
 
    #add up all hit and runs by town/city name and sort values in ascending order of hit and run
    sumHitAndRunbyTown = df[df['HIT_RUN_DESCR'] == "Yes, hit and run"].groupby('CITY_TOWN_NAME').size()
    sumHitAndRunbyTown = sumHitAndRunbyTown.sort_values()
    print(sumHitAndRunbyTown)
    
    #create a new figure and set up subplots (in this case, we only need one), ax refers to axes
    #this is included to comply with Streamlit soon requiring arguments for st.pyplot()
    fig, ax = plt.subplots()
    
    #initialize default value for color parameter
    color1 = ['gray', 'cyan', 'blue','darkblue']
    
    #creating bar chart of city town name by the sum of all hit and runs in that town
    ax.bar(sumHitAndRunbyTown.index, sumHitAndRunbyTown.values, color = color1 )
    #chart details
    plt.title("Total Hit-and-Runs by Town (for Selected Period)")
    plt.xlabel('Town/City Name')
    plt.xticks(rotation = 90, fontsize = 4)
    plt.ylabel("Total Hit-and-Runs")
    plt.yticks(np.arange(min(sumHitAndRunbyTown.values)-1, max(sumHitAndRunbyTown.values)+3, 5))
    
    st.pyplot(fig)
    
 

def distractedSpeedLimLine (df):
    '''
    @param: data frame
    @returns: N/a
    -This function creates a line chart comparing the speed limit to a sum of the instances of distracted 
    driving on roads with that speed limit. I included a button to remind the user not to drive distracted.
    -For this function's code, I used PlottingWithinStreamlit.py and streamlit's st.button page for guidance.
    '''
    #title
    st.markdown("<h1 style='color: darkblue; font-family: Times New Roman;'>Line Chart of Distracted Driving Crashes by Speed Limit</h1>", unsafe_allow_html=True)

    #initialize dictionary to count distracted driving instances per town
    distracted_driving_counts = {}
    
    #filter rows to only have those where "distracted" is included, regardless of whether it is upper or lowercase
    df_distracted = df[df['DRVR_CNTRB_CIRC_CL'].str.contains('Distracted', case=False)]
    
    #iterate through each driver contributing circumstance to find instances where "distracted" is included.
    #.unique() refers to all unique instances of speed limits within that column
    for lim in df_distracted['SPEED_LIM'].unique():
        
        # Count occurrences of distracted driving at each speed. The method .shape[0] refers to the number of rows 
        #in the filtered data frame, while .shape[1] would refer to the number of columns 
        DistDrivingCount = df_distracted[df_distracted['SPEED_LIM'] == lim].shape[0]
        distracted_driving_counts[lim] = DistDrivingCount


    #Convert the dictionary to DataFrame
    totDistDrivingPerSpeedLim = pd.DataFrame(list(distracted_driving_counts.items()), columns=['SPEED_LIM', 'DistDrivingCount'])
    #sort dataframe by road width, replacing the original data frame with the sorted one
    totDistDrivingPerSpeedLim.sort_values(by='SPEED_LIM', inplace=True)
    
    
    #create a new figure and set up subplots (in this case, we only need one), ax refers to axes
    #this is included to comply with Streamlit soon requiring arguments for st.pyplot()
    fig, ax = plt.subplots()
    
    #create color to be used for this line plot
    color1 = "darkblue"
    #create line plot
    ax.plot(totDistDrivingPerSpeedLim['SPEED_LIM'], totDistDrivingPerSpeedLim['DistDrivingCount'], color = color1)
    
    #fill space under line with light blue color
    ax.fill_between(totDistDrivingPerSpeedLim['SPEED_LIM'], totDistDrivingPerSpeedLim['DistDrivingCount'], color='lightblue')

    #chart details
    plt.title("Distracted Driver Car Crash Instances by Speed Limit")
    plt.xlabel("Speed Limit (MPH)")
    plt.ylabel("Total Distracted Driver Crash Incidents")
    plt.xticks(np.arange(min(totDistDrivingPerSpeedLim['SPEED_LIM']), max(totDistDrivingPerSpeedLim['SPEED_LIM'])+3, 5))
    plt.yticks(np.arange(min(totDistDrivingPerSpeedLim['DistDrivingCount'])-1, max(totDistDrivingPerSpeedLim['DistDrivingCount'])+3, 5))
    st.pyplot(fig)
    
                                                                                                             
    #create button to give user advice -- with balloons!
    st.button("Reset", type="primary")
    if st.button("Advice"):
        st.write("<p style='font-size: 24px;'>Do not drive distracted! Eyes on the road!</p>", unsafe_allow_html=True)
        st.balloons()



def main():
    
    #create side bar navigation, expanded, with a selectbox for various pages of the app
    st.set_page_config(initial_sidebar_state="expanded" )
    page = st.sidebar.selectbox("Select a page", ["Home", "Crashes Map by Severity", "Hit-and-Runs by Town and Date", "Distracted Driving by Speed Limit"])
    
    #read car crash sample data and apply the function to clean it
    Crashes= pd.read_csv("2017_Crashes_10000_sample.csv")
    Crashes = CleanedData(Crashes)
    
    #if/elif/else statement to navigate from page to page
    if page == "Home":
        introPage()
    elif page == "Crashes Map by Severity":
        crashMap(Crashes)
    elif page == "Hit-and-Runs by Town and Date":
        hitAndRunbar(Crashes)
    else: 
        distractedSpeedLimLine(Crashes)
    

main()




