BIN=node_modules/.bin

BROWSERIFY=$(BIN)/browserify
WATCHIFY=$(BIN)/watchify
BABEL=$(BIN)/babel
BROWSERSYNC=$(BIN)/browser-sync

JS_TARGET=dist/bundle.js
JS_APP=app/main.js


all: deps build

deps:
	npm install

build: $(JS_TARGET)

$(JS_TARGET): $(JS_APP)
	mkdir -p $(dir $@)
	$(BROWSERIFY) -t babelify -d $< --outfile $@
# 	$(BABEL) $@ > $@

dev: watch serve

watch:
	$(WATCHIFY) $(JS_APP) -o $(JS_TARGET)

sync:
	$(BROWSERSYNC) start --server --files="*.json,dist/*.js,*.html,css/*.css" --no-open

serve:
	python -m http.server

clean:
	rm $(JS_TARGET)
