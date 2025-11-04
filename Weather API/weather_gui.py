from tkinter import *
from tkinter import messagebox
from datetime import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from weather_api import get_weather_data

def create_gui():
    root = Tk()
    root.title("Weather App")
    root.geometry("900x500+300+200")
    root.resizable(FALSE, FALSE)

    def fetch_weather():
        try:
            city = textfield.get()

            geolocator = Nominatim(user_agent="geoapiExercises") #
            location = geolocator.geocode(city)
            obj = TimezoneFinder()
            result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
            
            home = pytz.timezone(result)
            local_time = datetime.now(home)
            current_time = local_time.strftime("%I:%M %p")
            clock.config(text=current_time)
            name.config(text="CURRENT WEATHER")

            weather = get_weather_data(city)

            t.config(text=(weather["temp"], "°"))
            c.config(text=(weather["condition"], "|", "FEELS", "LIKE", weather["temp"], "°"))
            w.config(text=weather["wind"])
            h.config(text=weather["humidity"])
            d.config(text=weather["description"])
            p.config(text=weather["pressure"])

        except Exception as e:
            messagebox.showerror("Weather App", f"Ocurrió un error:\n{e}")

    # Interfaz
    global textfield, clock, name, t, c, w, h, d, p

    search_image = PhotoImage(file="img/search.png")
    Label(image=search_image).place(x=20, y=20)

    textfield = Entry(root, justify="center", width=27, font=("poppins", 15, "bold"), bg="#404040", border=0, fg="white")
    textfield.place(x=50, y=40)
    textfield.focus()

    search_icon = PhotoImage(file="img/search_icon.png")
    Button(image=search_icon, borderwidth=0, cursor="hand2", bg="#404040", command=fetch_weather).place(x=400, y=33)

    Logo_image = PhotoImage(file="img/logo.png")
    Label(image=Logo_image).place(x=150, y=100)

    Frame_image = PhotoImage(file="img/box.png")
    Label(image=Frame_image).pack(padx=5, pady=5, side=BOTTOM)

    name = Label(root, font=("arial", 14, "bold"))
    name.place(x=30, y=100)
    clock = Label(root, font=("Helvetica", 18))
    clock.place(x=30, y=130)

    Label(root, text="WIND", font=("Helvetica", 14, "bold"), fg="white", bg="#1ab5ef").place(x=120, y=400)
    Label(root, text="HUMIDITY", font=("Helvetica", 14, "bold"), fg="white", bg="#1ab5ef").place(x=250, y=400)
    Label(root, text="DESCRIPTION", font=("Helvetica", 14, "bold"), fg="white", bg="#1ab5ef").place(x=430, y=400)
    Label(root, text="PRESSURE", font=("Helvetica", 14, "bold"), fg="white", bg="#1ab5ef").place(x=650, y=400)

    t = Label(font=("arial", 66, "bold"), fg="#ee666d")
    t.place(x=400, y=150)
    c = Label(font=("arial", 14, "bold"))
    c.place(x=400, y=250)

    w = Label(text="...", font=("arial", 18, "bold"), bg="#1ab5ef")
    w.place(x=120, y=430)
    h = Label(text="...", font=("arial", 18, "bold"), bg="#1ab5ef")
    h.place(x=280, y=430)
    d = Label(text="...", font=("arial", 18, "bold"), bg="#1ab5ef")
    d.place(x=450, y=430)
    p = Label(text="...", font=("arial", 18, "bold"), bg="#1ab5ef")
    p.place(x=670, y=430)

    root.mainloop()
