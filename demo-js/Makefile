BIN=node_modules/.bin

BROWSERIFY=$(BIN)/browserify

JS_TARGET=dist/bundle.js
JS_APP=app/main.js


all: deps build

deps:
	npm install

build: $(JS_TARGET)

$(JS_TARGET): $(JS_APP)
	mkdir -p $(dir $@)
	$(BROWSERIFY) -t babelify -d $< --outfile $@

clean:
	rm $(JS_TARGET)
