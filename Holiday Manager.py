#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass

# -------------------------------------------
#creating holiday dataclass
@dataclass
class Holiday:
    
    #class attributes
    name: str
    date: datetime.datetime

    # String output method
    def __str__ (self):
        return self.name+': {}'.format(self.date)

#creating HolidayList class
class HolidayList:
    
    #setting constructor
    def __init__(self):
        self.innerHolidays = []
    
    #function to add newly created holiday objects to innerHoliday List
    def addHoliday(self, holidayObj):
        self.innerHolidays.append(holidayObj)
    
    #function to create new holiday objects and using addHoliday function adding it to innerHoliday List
    def add_holiday(self):
        print()
        print('Add a Holiday\n===============\n')
        condition = False
        while condition is False:
            holiday_name = input('Holiday: ')
            while True:
                holiday_date = input('Date (yyyy-mm-dd): ')
                try :
                    holiday_date = datetime.datetime.strptime(holiday_date, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Error: must be format yyyy-mm-dd ")
            holidayObj = Holiday(holiday_name, str(holiday_date))
            self.addHoliday(holidayObj)
            print(f'Success:\n{holiday_name} ({holiday_date}) has been added to the list\n')
            repeat = input('Do you want to add more holiday to the list? Y/N').upper()
            if repeat == 'Y':
                condition = False
            else:
                print()
                condition = True
    
    #function to find holiday object within innerHoliday List and returning it for user
    def findHoliday(self):
        condition = False
        while condition is False:
            holiday_name = input('Please input your holiday name: ')
            while True:
                date = input('Please input your holiday date (yyyy-mm-dd): ')
                try:
                    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Error: must be format yyyy-mm-dd ")
            if Holiday(holiday_name, str(date)) in self.innerHolidays:
                return Holiday(holiday_name, str(date))
                condition = True
            else:
                print(f'Error:\n{holiday_name} not found. Please try again\n')
                condition = False
                           
                    
    #function to remove holiday object from innerHoliday list. Using findHoliday function to locate the target object
    def removeHoliday(self):
        print()
        print('Remove a Holiday\n===============\n')
        holiday = self.findHoliday()
        self.innerHolidays.remove(holiday)
        print(f'Success:\n{holiday} has been removed from the holiday list\n')
    
    #function to open provided json file, converting its elements into holiday objects and using addHoliday function 
    #adding them into innerHoliday list
    def read_json(self, filelocation):
        with open(filelocation) as json_file:
            data = json.load(json_file)
            for x in data['holidays']:
                this = Holiday(x['name'],x['date'])
                self.addHoliday(this)
        
    #function to create "sample" json file and writing innerHoliday list in it and saving it using json.dumps()
    def save_to_json(self):
        print()
        print('Saving Holiday List\n===============\n')
        condition = False
        while condition is False:
            save_changes = input('Are you sure you want to save your changes? y/n').lower()
            if not save_changes.isalpha():
                print('That was invalid entry. Please try again [y/n]')
            else:
                condition = True
        if save_changes != 'y':
            print('Canceled\nHoliday list file save canceled')
        else:
            new_list = []
            new_dict = {}
            for obj in self.innerHolidays:
                new_list.append({'name':obj.name, 'date':obj.date})
            new_dict['holidays']=new_list
            json_object = json.dumps(new_dict, indent = 4) 
            with open("sample.json", "w") as outfile:
                outfile.write(json_object)
            print('Success:\nYour changes have been saved\n')
            
    #function for scraping holiday names and dates from https://www.timeanddate.com/holidays/us using request module
    #and bs4 modules to acomplish it.
    def scrapeHolidays(self, url, year):
        my_request = requests.get(url)
        parser = BeautifulSoup(my_request.content, 'html.parser')
        table = parser.find('article',attrs = {'class':'table-data'})
        test_list_holidays = []
        test_list_date = []
        dict_2020 = {}
        for temporary in parser.select('a:-soup-contains("(Tentative Date)")'):
            temporary.decompose()
        for row in table.find_all_next('tbody'):
            us_rows = row.select('a[href *= "/holidays/us/"]')
            for holiday in us_rows:
                test_list_holidays.append(holiday.text)
                date = holiday.find_previous().find_previous().find_previous()
                date = date.getText() + f" {year}"+' 09:00AM'
                format = '%b %d %Y %I:%M%p'
                date = str(datetime.datetime.strptime(date, format).date())
                test_list_date.append(date)
        dict_2020 = dict(zip(test_list_holidays, test_list_date))
        new_list = []
        
        for key, value in dict_2020.items():
            new_list.append({'name':key, 'date': value})

        return new_list
    
    #function to filter holidays based on user desired year and week using datetime module. 
    #first created list of week dates based on year and week number inputed by user
    #second using lambdas filtered holiday objects in innerHoliday list based on matching elements with list of dates created
    #Didn't need to use displayHolidaysInWeek function, since i could just print results within this function
    def filter_holidays_by_week(self, year, week_number):
        first = datetime.datetime.strptime(f'{year}-W{int(week_number)-1}-1', "%Y-W%W-%w").date()
        second = first+datetime.timedelta(days=1)
        third = first+datetime.timedelta(days=2)
        forth = first+datetime.timedelta(days=3)
        fifth = first+datetime.timedelta(days=4)
        sixth = first+datetime.timedelta(days=5)
        seventh = first+datetime.timedelta(days=6)
        week_dates = [str(first), str(second), str(third), str(forth), str(fifth), str(sixth), str(seventh)]
        
        holidays = list(filter(lambda obj: obj.date in week_dates, self.innerHolidays))
        
        for obj in holidays:
            print(f'{obj.name} ({obj.date})')
        print()

        
    #function to get user input for year and week number and using filter_holidays_by_week function displaying matched results 
    def viewCurrentWeek(self):
        condition = False
        while condition is False:
            print()
            print('View Holidays\n===============\n')
            year = input('Which year?: ')
            week_number = input('Which week? #[1-52, leave blank for the current week]: ')
            print()
            if not year.isnumeric():
                print('Please input year in four digits.')
            elif not week_number.isnumeric():
                print('Please input week number as a digit.')
            elif len(week_number) == 0:
                my_date = datetime.date.today()
                year1, week, day = my_date.isocalendar()
                week_number = str(week)
                year = str(year1)
                condition = True
            else:
                condition = True
            print(f'These are the holidays for {year} week #{week_number}\n')
            self.filter_holidays_by_week(year, week_number)
        
        
    #funtion to get user input for menu selection and validate the input            
    def menu_selection(self):
        condition = False
        while condition is False:
            selection = input('Please make a selection from the menu number (1-5): ')
            if not selection.isnumeric():
                print('That was not a valid menu number selection. Please try again')
            elif selection not in ('1','2','3','4','5'):
                print('That was not a valid menu number selection. Please try again')
            else:
                condition = True
        return selection


# Main function to run the programm and call appropriate methods from HolidayList class 
def main():    
    
    # 1. Initialize HolidayList Object
    holList = HolidayList()
    
    # 2. Load JSON file via HolidayList read_json function
    holList.read_json('Holidays.json')

    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    scrape_2020 = holList.scrapeHolidays("https://www.timeanddate.com/holidays/us/2020", "2020")

    scrape_2021 = holList.scrapeHolidays("https://www.timeanddate.com/holidays/us/2021", "2021")

    scrape_2022 = holList.scrapeHolidays("https://www.timeanddate.com/holidays/us/2022", "2022")
    
    scrape_2023 = holList.scrapeHolidays("https://www.timeanddate.com/holidays/us/2023", "2023")

    scrape_2024 = holList.scrapeHolidays("https://www.timeanddate.com/holidays/us/2024", "2024")
    
    # 4. combine all scraped date into one list 
    total_list = scrape_2020+scrape_2021+scrape_2022+scrape_2023+scrape_2024

    # 5. conver craped data into holiday objects and load it into innerHoliday list
    master_list = []
    master_list.append({'holidays':total_list})
    for x in master_list[0]['holidays']:
        this = Holiday(x['name'],x['date'])
        holList.addHoliday(this)
    
    # 5. main menu loop, keeps running until user exits
    exitCondition = False
    while exitCondition is False:
        
        # 6. Display User Menu (Print the menu)
        print('MAIN MENU\n===================\nHoliday Menu\n')
        print('1. Add a Holiday')
        print('2. Remove a Holiday')
        print('3. Save Holiday list')
        print('4. View Holidays')
        print('5. Exit')
        
        # 7. get user input for menu selection. validate the input. assign it to user_input variable
        user_input = holList.menu_selection()
        
        # 8. chain of operations based on user_input
        if user_input == '1':
            holList.add_holiday()
        elif user_input == '2':
            holList.removeHoliday()
        elif user_input == '3':
            holList.save_to_json()
        elif user_input == '4':
            holList.viewCurrentWeek()
        elif user_input == '5':
            
            # 9. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 
            print('Exit\n=====\n')
            if len(holList.innerHolidays) == 1333:
                condition1 = False
                while condition1 is False:
                    question = input('Are you sure you want to exit? [y/n]: ').lower()
                    if not question.isalpha():
                        print('That was invalid input. Please try again [y/n]')
                    elif question == 'y':
                        print('Goodbye')
                        condition1 = True
                        exitCondition = True
                    else:
                        condition1 = True
                        exitCondition = False
            else:
                condition2 = False
                while condition2 is False:
                    question1 = input('Are you sure you want to exit?\nYour changes will be lost.\n[y/n]: ').lower()
                    if not question1.isalpha():
                        print('That was invalid input. Please try again [y/n]')
                    elif question1 == 'y':
                        print('Goodbye')
                        condition2 = True
                        exitCondition = True
                    else:
                        condition2 = True
                        exitCondition = False
                        
                        
main()


# In[ ]:





# In[ ]:


s


# In[ ]:




