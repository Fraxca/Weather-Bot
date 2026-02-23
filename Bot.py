import discord
from discord.ext import commands, tasks
import requests
import os
from dotenv import load_dotenv

load_dotenv() 

intents = discord.Intents.default() 
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado")

@bot.event
async def on_member_join(member:discord.Member):
    canal = bot.get_channel(1474225698741813290)
    await canal.send(f"{member.mention} entrou no servidor")
    

@bot.command()
async def metar(ctx, *, icao: str = None):
    if not icao:
        await ctx.send(" Use: `!metar <CÓDIGO_ICAO>`\n\nExemplos:\n`!metar KJFK` (Nova York)\n`!metar SBSP` (São Paulo)\n`!metar EGLL` (Londres)")
        return
    
    try:
        url = f"https://avwx.rest/api/metar/{icao.upper()}"
        headers = {"Authorization": "Token XzgujcZkazo_63sa1o3lgNjqu8U_jLsI9Doh1yDHGcw"} 
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraindo dados
            icao_code = data.get("icao", "N/A")
            raw = data.get("raw", "N/A")
            
            # Temperatura
            temp = data.get("temp", {})
            temp_val = "N/A"
            if isinstance(temp, dict):
                temp_val = temp.get("value", "N/A")
            elif isinstance(temp, (int, float)):
                temp_val = temp
            
            # Vento
            wind = data.get("wind_speed", {})
            wind_val = "N/A"
            wind_unit = "kt"
            if isinstance(wind, dict):
                wind_val = wind.get("value", "N/A")
                wind_unit = wind.get("unit", "kt")
            
            # Direção do vento
            wind_dir = data.get("wind_direction", {})
            wind_dir_val = "N/A"
            if isinstance(wind_dir, dict):
                wind_dir_val = wind_dir.get("value", "N/A")
            
            # Pressão
            pressure = data.get("altimeter", {})
            pres_val = "N/A"
            pres_unit = "hpa"
            if isinstance(pressure, dict):
                pres_val = pressure.get("value", "N/A")
                pres_unit = pressure.get("unit", "hpa")
            
            # Visibilidade
            visibility = data.get("visibility", {})
            vis_val = "N/A"
            vis_unit = "m"
            if isinstance(visibility, dict):
                vis_val = visibility.get("value", "N/A")
                vis_unit = visibility.get("unit", "m")
            
            # Pista em uso (runway)
            runway = data.get("runway", "N/A")
            if isinstance(runway, dict):
                runway = runway.get("value", "N/A")
            elif isinstance(runway, list) and runway:
                runway = runway[0].get("value", "N/A") if isinstance(runway[0], dict) else runway[0]
            
            # Criando Embed
            embed = discord.Embed(
                title=f"METAR {icao.upper()}",
                description=raw,
                color=discord.Color.blue()
            )
            
            # Adicionando campos
            embed.add_field(name=" Temperatura", value=f"{temp_val} °C", inline=True)
            embed.add_field(name=" Vento", value=f"{wind_val} {wind_unit}", inline=True)
            embed.add_field(name=" Direção do Vento", value=f"{wind_dir_val}°", inline=True)
            embed.add_field(name=" Pressão", value=f"{pres_val} {pres_unit}", inline=True)
            embed.add_field(name=" Visibilidade", value=f"{vis_val} {vis_unit}", inline=True)
            embed.add_field(name=" Pista em Uso", value=f"{runway}", inline=True)
            
            embed.set_footer(text="Dados obtidos de AVWX REST API")
            await ctx.send(embed=embed)
            
        elif response.status_code == 401:
            await ctx.send(" Erro de autenticação na API. Token inválido.")
        elif response.status_code == 404:
            await ctx.send(f" Código ICAO '{icao.upper()}' não encontrado.")
        else:
            await ctx.send(f" Erro ao obter METAR. Status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        await ctx.send(" Tempo limite excedido ao buscar METAR.")
    except Exception as e:
        await ctx.send(f" Erro: {str(e)}")
        print(f"Erro no comando metar: {e}")


@bot.command()
async def taf(ctx, *, icao: str = None):
    if not icao:
        await ctx.send(" Use: `!taf <CÓDIGO_ICAO>`\n\nExemplo:\n`!taf SBSP` (São Paulo)")
        return

    try:
        url = f"https://avwx.rest/api/taf/{icao.upper()}"
        headers = {"Authorization": "Token XzgujcZkazo_63sa1o3lgNjqu8U_jLsI9Doh1yDHGcw"}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            icao_code = data.get("icao", icao.upper())
            raw = data.get("raw", "N/A")

            embed = discord.Embed(
                title=f"TAF {icao.upper()}",
                description=raw,
                color=discord.Color.green()
            )

            embed.set_footer(text="Dados obtidos de AVWX REST API")
            await ctx.send(embed=embed)

        elif response.status_code == 401:
            await ctx.send(" Erro de autenticação na API. Token inválido.")
        elif response.status_code == 404:
            await ctx.send(f" Código ICAO '{icao.upper()}' não encontrado.")
        else:
            await ctx.send(f" Erro ao obter TAF. Status: {response.status_code}")

    except requests.exceptions.Timeout:
        await ctx.send(" Tempo limite excedido ao buscar TAF.")
    except Exception as e:
        await ctx.send(f" Erro: {str(e)}")
        print(f"Erro no comando taf: {e}")


token = os.getenv("DISCORD_TOKEN")

bot.run(token)