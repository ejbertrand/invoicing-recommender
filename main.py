# 0. Changed the importing declaration of the website package
import website as web

app = web.create_app()

if __name__ == "__main__":
	app.run(debug = True) # Have to change it to False when in production
