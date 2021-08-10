from quart import Quart, redirect, url_for , request , render_template , session
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import requests
from discord.ext import ipc


HOST = "0.0.0.0"
SECRET_KEY = "JATIN"

app = Quart(__name__)
ipc_client = ipc.Client(host=HOST,secret_key=SECRET_KEY)

app.config["SECRET_KEY"] = "test123" 
app.config["DISCORD_CLIENT_ID"] = 815136715155963924   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "o2nabMufqmu9t7DES-6c7S08Bp15mA2E"                # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "http://52.3.231.173/callback"                 # URL to your callback endpoint.

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
    return await render_template("home.html")


@app.route("/login/")
async def login():
    return await discord.create_session(scope = scope)
	

@app.route("/callback/")
async def callback():
    code = request.args.get("code")
    token = get_access_token(code)
    token = {"access_token": token}
    session["DISCORD_OAUTH2_TOKEN"] = token

    return redirect(url_for("servers"))

@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    return redirect(url_for("login"))

@app.route("/servers/")
@requires_authorization
async def servers():
    print(session["DISCORD_OAUTH2_TOKEN"])
    guild_count = await ipc_client.request("get_guild_count")
    guild_ids = await ipc_client.request("get_guild_ids")

    user_guilds = await discord.fetch_guilds()

    guilds = []

    for guild in user_guilds:
        if guild.permissions.administrator:			
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)

    guilds.sort(key = lambda x: x.class_color == "red-border")
    name = (await discord.fetch_user()).name
    return await render_template("dashboard.html", guild_count = guild_count, guilds = guilds, username=name)


@app.route("/dashboard/<int:guild_id>")
@requires_authorization
async def dashboard_server(guild_id):
	guild = await ipc_client.request("get_guild", guild_id = guild_id)
	if guild is None:
        #Redirect to add the bot in the server!  #change the below perms 8 as u wish 8 == admin 
		return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
	return guild["name"]








#NO NEED OF THIS SINCE WE ARE USING HYPERCORN TO DEPLOY BY QUART
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) #DEBUG MODE

#-------------------------------NOTES-------------------------------------------------
#at login if alr login show mange dashboard instaed of login


# BEFORE REDIRECT T AUTHORESE CHEKC IF ARL THERE IN SESSION AND CAN BE ABLE TO BE USED 

#if any case of username chagne or pass then promto to redirect to login 

#error with user redirect to login

