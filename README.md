# JSAnalyser_sublime_plugin
it is a sublime plugin for JavaScript code analysis


Installation process

step 1. Download all the dependencies

        open cmd or Powershell
        
        --> npm install -g eslint
  
        --> npm install -g eslint-plugin-angular
  
        --> npm install -g eslint-config-angular
  

step 2. Download/clone the repository

step 3. copy the repository to sublime package Location

        ->> Open sublime Text 

        ->> click on preferences -> Browse packages

        ->> copy the downloaded package to the opened file location from last step


->> Your plugin is installed...

->> click on Tools in sublime Text window

->> click on JSAnalyser

->> functionalities

  1. Run analyser on JS file
        
        ->> Analyser runs on save event ("control+s" and "control+j") 
  
  2. configure Rules
  
        ->> click on Tools -> JSAnalyser -> Configure Rules
        ->> select the rules and its configuration (Error,Warning,Off)
        ->> Click on finish and save the Configuration as JSON file.
  
  
  3. import your custom Rules file
            
        ->> click on Tools -> JSAnalyser -> Import configuration file
        ->> select JSON file

  4. Reset the configuration ( switch back to default configuration )
        
  5. Create Rule
        
        ->> prompt asks for Rule Name and Description 
        ->> Creates custom rule which consists of a folder which contains 4 files
            i.   rule file (rule_name.js)
            ii.  rule test file ( rule_nametest.js)
            iii. json configuration file for rule (rule_nameconfig.json)
            iv.  json metadata file for (rule_namemetadata.json)
  
  6. Select and Test Rule
        
         ->> select Ruleconfig file from the prompt 
         ->> Analyser runs on present file only for that rule.(recommend to run on rule_nametest.js file)
         ->> selected Config file will be set as the default test rule configuration.
         
  7. Test Rule
      
         ->> No need to select the ruleConfig again for testing.
         ->> previously selected ruleConfig file will be used for testing.
         
  8. Import Rule
  
         ->> Import the tested rule to global configuration as official custom rule for linting.  
