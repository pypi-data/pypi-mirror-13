# Webmaster

A packages included Flask based framework to rapidly develop web applications 
and API endpoints. 

It comes with User Login section, Admin section to quickly get you going.

Also it includes a CMS admin, to quickly post blogs, create dynamic pages on the site.

Version: 0.0.*

## Install

    pip install webmaster --process-dependency-links
    
## Create a new app

    cd your_dir 
    
    wp create -a www
    
## Setup Project
    
    cd your_dir 
    
    python manage.py setup
    
### Start your server

    wp serve -a www

Go to http://127.0.0.1:5000/

---
    
## Why Flask?

Because Flask is fun, and you will still feel like you are writing. Explicity


## Why not Django? 

Because it's not Django. That's it! 


## Decision Made for You

- Smart routing: automatically generates routes based on the classes and methods in your views
    
- Class name as the base url, ie: class UserAccount will be accessed at '/user-account'

- Class methods (action) could be accessed: hello_world(self) becomes 'hello-world'

So

    class UserAccount(Webmaster):
        
        def hello_world(self):
            return {}

Will be accessed at **/user-account/hello-world**

- Easy rending and render decorator

By default views methods can return a dict and it will transform to the rendering views

    class Index(Webmaster):
    
        # url: /
        def index(self):
            return {
                "name": "John Doe",
                "location": "World"
            }


        # url: /hello-world
        @render_as_json
        def hello_world(self):
            return {
                "city": "Charlotte",
                "state": "North Carolina"
            }
            
        
        # url: /another-one-as-xml
        @render_as_xml
        def another_one_as_xml(self):
            return {
                "city": "Charlotte",
                "state": "North Carolina"
            }


- Auto route can be edited with @route()

- Restful: GET, POST, PUT, DELETE

- API Ready

- bcrypt is chosen as the password hasher

- Session: Redis, AWS S3, Google Storage, SQLite, MySQL, PostgreSQL

- ORM: Active Alchemy (SQLALchemy wrapper)

- ReCaptcha

- csrf on all POST

- CloudStorage: Local, S3, Google Storage

- mailer (SES or SMTP)

- Caching

- Recaptcha

- Propel for deployment



# Built-in Packages

- Basic Layout

- Index page

- Login, Signup, Lost Password, Account Settings page

- User Admin

- CMS Post Admin (To manage posts (article, blog, dynamic pages))

- Post Reader (To read post)

- Contact Page

- Error Page (Custom error page)

- Social Signin (in experiment)

- Social Share

- Bootswatch

- Font-Awesome

- Markdown


# Front End Components

- Lazy load images

- Social Share Buttons


---
 
Application Structure:

    /application
    
        - /data
        
            - /mailer-templates
            
            - /uploads
        
        - /extras
        
            - __init__.py
        
        - /www
        
            - /static
                
                - /css
                
                - /images
                
                - /js
                
                - assets.yml
                
            - /templates
            
                - /Index
                    
                    - index.html
            
            - __init__.py
            
            - views.py
        
    - manage.py
    
    - propel.yml
    
    - requirements.txt
    
    - serve_www.py


---


Core Modules:

    webmaster.core
    
    webmaster.decorators
    
    webmaster.ext
    
    webmaster.packages
    
    