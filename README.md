# Simple AI integrated automatic IELTS writing evaluator
##########################################################

# Description
Using flask framework, Llama AI fro G4F library and MongoDB for remote database and telegram open API to automate the process of evaluation of writing tasks in IELTS.

# Deployment
1. ## Clone/Fork this repository
2. ## MongoDB
   - Create database 'writing-check' and collection 'users'
3. ## Environmental variables
   - ADMIN - your telegram ID
   - BOT_TOKEN - your telegram bot's ID
   - GROUP - telegram group ID for sending data (not functional!)
   - PASSWORD - MongoDB password
   - USERNAME - MongoDB username
   - TASK_ONE - copy from assets/task_one.txt
   - TASK_TWO - copy from assets/task_two.txt
   
# Future Plans
- *Graphical evaluation on writing task 1*
- *Training the model with large dataset*
- *Including other test formats*
