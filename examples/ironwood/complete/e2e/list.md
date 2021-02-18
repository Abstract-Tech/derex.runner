# Tests list

## LMS

### Authentication (requires access to emails)
* As an anonymous user I should be able to register an account 
* As an anonymous user I should be able to login 

### Account settings app
* As a logged in user I should be able to edit my profile informations from the account settings app 
* As a logged in user I should be able to to delete my account from the account settings app

### User Profile app
* As a logged in user I shouldn't be able to edit my profile if my date of birth is unspecified 
* As a logged in user I should be able to upload an avatar image if my date of birth is specified 
* As a logged in user I should be able to add a description in the "About me" section if my date of birth is specified 

### Courses catalog
* As an anonymous user I should be able to browse the course catalog

### Dashboard
* As a logged in user I should be able to enroll in a course and have it displayed in my dashboard
* As a logged in user I should be able to access the courseware of a course i'm enrolled in from my dashboard 
* As a logged in user I should be able to unenroll from a course i'm enrolled in from my dashboard 

### Courseware
* As a logged in user I should be able to access the courseware of a course i'm enrolled in ✓
* As a logged in user I should be able to access the "Wiki" tab of the courseware of a course i'm enrolled in 
* As a logged in user I should be able to access the "Progess" tab of the courseware of a course i'm enrolled in 
* As a logged in user I shouldn't be able to access the "Instructor" tab of the courseware of a course i'm enrolled in 
* As a logged in user with standard privileges I shouldn't be able to access the "Instructor" tab of the courseware of a course i'm enrolled in
* As a logged in user with admin or staff privileges I should be able to access the "Instructor" tab of the courseware of a course i'm enrolled in
* As a logged in user I should be able to access additional pages tabs of the courseware of a course i'm enrolled in
* As a logged in user I should be able to submit problem responses and obtain consistent feedback

### Instructor dashboard
* 

## CMS
### Authentication + Authorization
* they are tested in LMS

### Course authoring
* As a logged in user with admin on a course I should be able to create chapters, sections and units 
* As a logged in user with admin on a course I should be able to see a preview of the units on the LMS 
* As a logged in user with admin on a course I should be able to reindex course data if `ENABLE_COURSE_DISCOVERY` feature is enabled 
* As a logged in user with admin on a course I should be able to publish course units in draft status 
* As a logged in user with admin on a course I should be able to set course schedule and details informations 
* As a logged in user with admin on a course I should be able to upload a course card image from the course "Schedule and details" 
* As a logged in user with admin on a course I should be able to set a grading policy for the course
