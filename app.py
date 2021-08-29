from datetime import timedelta
from quart import Quart, redirect, url_for , request , render_template , session
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import requests
from discord.ext import ipc
from pymongo import MongoClient



from dotenv import dotenv_values
VALUES = dotenv_values("paradox-bot-ipc/ipc-venv/.env")
cluster = MongoClient(VALUES["DB_URI"])


HOST = VALUES["SERVER_IP"] #CHAGNGE IP AND PASS LATER LOL
SECRET_KEY = VALUES["SERVER_PASS"]        

app = Quart(__name__)
ipc_client = ipc.Client(host=HOST,secret_key=SECRET_KEY)

app.permanent_session_lifetime = timedelta(hours= 12)

app.config["SECRET_KEY"] = VALUES["SECRET_KEY"]
app.config["DISCORD_CLIENT_ID"] = VALUES["CLIENT_ID"]   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = VALUES["CLIENT_SECRET"]                # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = f"http://{HOST}:8080/callback"                 # URL to your callback endpoint.

discord_token_url = "https://discord.com/api/oauth2/token"
discord_api_url = "https://discord.com/api"
scope=['identify', 'email', 'guilds']
discord = DiscordOAuth2Session(app)




def get_access_token(code):
    payload = {
        "client_id": app.config["DISCORD_CLIENT_ID"],
        "client_secret": app.config["DISCORD_CLIENT_SECRET"],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": app.config["DISCORD_REDIRECT_URI"],
        "scope": scope
    }

    access_token = requests.post(url = discord_token_url, data = payload).json()
    return access_token.get("access_token")




def get_user_json(access_token):
    url = f"{discord_api_url}/users/@me"
    headers = {"Authorization": f"Bearer {access_token}"}

    user_object = requests.get(url = url, headers = headers).json()
    return user_object

@app.route("/")
@app.route("/home")
async def home():
    authorized = True if "DISCORD_OAUTH2_TOKEN" in session else False 
    return await render_template("home.html", user = session["username"])


@app.route("/login/") #What if already logged in and again created a new session?
async def login():#flash redirecting to discord
    return await discord.create_session(scope = scope)
	
@app.route("/logout")
async def logout(): #flash logged out
    session.pop("DISCORD_OAUTH2_TOKEN")
    return redirect(url_for('home'))

@app.route("/callback/")
async def callback():
    code = request.args.get("code")
    token = get_access_token(code)
    token = {"access_token": token}
    session["DISCORD_OAUTH2_TOKEN"] = token

    user = await discord.fetch_user()

    guild_ids = await ipc_client.request("get_guild_ids")
    user_guilds = await discord.fetch_guilds()
    guilds = []

    for guild in user_guilds:
        if guild.permissions.administrator:			
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)

    guilds.sort(key = lambda x: x.class_color == "red-border")


                         

    session["username"] = user.name + "#" + user.discriminator
    #session["guilds"] = guilds

    return redirect(url_for("user_module"))

@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return redirect(url_for("login"))




@app.route("/dashboard/")
@app.route("/dashboard/me")
@app.route("/dashboard/me/<module>")
@requires_authorization
async def user_module(module="user_overview"):
    if module == "logout": return redirect(url_for('logout'))
    user = await discord.fetch_user()

    try:

        guilds = session["guilds"]
        username = session["username"]
    except:
        guild_ids = await ipc_client.request("get_guild_ids")
        user_guilds = await discord.fetch_guilds()
        guilds = []

        for guild in user_guilds:
            if guild.permissions.administrator:			
                guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
                guilds.append(guild)
        guilds.sort(key = lambda x: x.class_color == "red-border")

    
    

    #put random things at end of the suer for fun and in the drop down add teh user id also for some reason i like seing user id as more inof SHUT!
    return await render_template(f"{module}.html", guilds = guilds,user= user, user_comment="noob", title="Dashboard")




        

@app.route("/dashboard/<int:guild_id>", methods= ['POST', 'GET'])
@app.route("/dashboard/<int:guild_id>/<module>", methods= ['POST', 'GET'])
@requires_authorization #bro if not autho then redirect to a diffrent page instead of sending them to discord like serioulsy
async def dashboard_modules(guild_id, module="overview"):

    if request.method == 'POST':
        data = await request.form
        print("[PAYLOAD RECIVED]", data.keys())



        payload = {
                "_id": guild_id,
                "prefix": ".",
                "roles": {},
                "channels": {},
                "leveling": {
                    "no_xp_channels": [],
                    "no_xp_roles":[] ,
                    "xp_rate": "1", 
                    "action_on_level_up": None, 
                    "level_reward": None,
                    "leveling_enabled": "off", 
                    "len_levels": 0,
                    },
                "moderation": {},
            }

                
        if module == 'leveling':
            print("module leveling")
            levels_list = []
            roles_list = []
            level_reward_list = []
            for i in data.keys():
                #(level, roleid)
                if i.startswith("entry"):
                    if data[i].startswith("Level"):
                        levels_list.append(i)
                    else:
                        roles_list.append(i)



                        
                else:
                    payload["leveling"][str(i)] = data[i]
                    
            for x in levels_list:
                for y in roles_list:
                    if x.split(",")[0] == y.split(",")[0]:
                        level_reward_list.append((x.split(",")[1], y.split(",")[1], data[y]  ))


            payload["leveling"]['no_xp_channels'] = data.getlist('no_xp_channels')
            payload["leveling"]['no_xp_roles'] = data.getlist('no_xp_roles')
            payload["leveling"]["level_reward"] = level_reward_list
            payload['leveling']['len_level'] = len(level_reward_list)
            print("[PAYLOAD SENT]",payload)  
            #logging


            
            await ipc_client.request(
                "update_guild_configs",
                guild_id = guild_id,
                module= module,
                data = payload
            )
            print("[DB UPDATED]")
            

    user = await discord.fetch_user() #nickname / comment

    try:
        guilds = session["guilds"]
        username = session["username"]
    except:
        guild_ids = await ipc_client.request("get_guild_ids")
        user_guilds = await discord.fetch_guilds()
        guilds = []

        for guild in user_guilds:
            if guild.permissions.administrator:			
                guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
                guilds.append(guild)
        guilds.sort(key = lambda x: x.class_color == "red-border")




    guild_channels = await ipc_client.request(
        "get_guild_channels",
        guild_id=guild_id)
    # [(category, [ch1, ch2, ch3])]

    guild_roles = await ipc_client.request(
        "get_guild_roles",
        guild_id = guild_id
    )
    

    

    print("Requesting IPC Server for guild_configs")

    #ratelimition
    #too many requests
    #429
    guild_configs = await ipc_client.request(
        "get_guild_configs",
        guild_id = guild_id
    )

    guild_configs['leveling']['len_level'] = len(guild_configs['leveling']['level_reward'])
    print("Fetched Latest Data")

    return await render_template(
        f"{module}.html", guilds= guilds,
        user= user, title= "Leveling-Dashboard", username = "username",
        guild_id=guild_id, module=module,
        guild_channels = guild_channels, guild_roles= guild_roles, 
        guild_configs = guild_configs
        )

        #This is only for Leveling Module rn 
        #finish all inputs and styling of leveling 
        #then guilds_genral 
        #guilds_send embed accept pastebin or JSOn discord supported later dot i
        #Lfg private PLX 

        #me/user_id
        #homepage cool animations
        #domain name
        #ai paradox
        #backup (cryptography security  , privacy)






@app.route("/dev")
async def devpage():
    test = await ipc_client.request(
        "thebiggesttest"
    )
    print(test)
    return "yo dev U FUCKING NERD"





#NO NEED OF THIS SINCE WE ARE USING HYPERCORN TO DEPLOY BY QUART
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) #DEBUG MODE

#-------------------------------NOTES-------------------------------------------------
#at login if alr login show mange dashboard instaed of login


# BEFORE REDIRECT T AUTHORESE CHEKC IF ARL THERE IN SESSION AND CAN BE ABLE TO BE USED 

#if any case of username chagne or pass then promto to redirect to login 

#error with user redirect to login



    #benifits 
    #premium custom
    #custom bot 
    #maintaince 
    #hosting 
   # personalised contorl pannel for the guild
    #guild stats on webpage
    #role and stuff