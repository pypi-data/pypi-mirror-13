PACKAGE_NAME:=rrn_kr
PACKAGE_VERSION:=0.0.0
SRC_DIR:=rrn_kr
LOCALE_DIR:=rrn_kr/locale
DOMAIN:=rrn_kr
LANGUAGES:=en ko
MAINTAINER:=mete0r@sarangbang.or.kr
POT_FILE:=$(LOCALE_DIR)/$(DOMAIN).pot
PO_FILES:=$(addprefix $(LOCALE_DIR)/,$(LANGUAGES))
PO_FILES:=$(addsuffix /LC_MESSAGES/$(DOMAIN).po,$(PO_FILES))
MO_FILES:=$(addsuffix .mo,$(basename $(PO_FILES)))

define create-pot
	echo ' CREATE-POT ' $@
	bin/pot-create --domain $(DOMAIN) --package-name $(PACKAGE_NAME) --package-version $(PACKAGE_VERSION) --msgid-bugs-address $(MAINTAINER) --sort-by-file --output $@ $(SRC_DIR)
endef

define create-po
	echo '  MSGINIT   ' $@
	[ -d $(dir $@) ] || mkdir -p $(dir $@)
	msginit --input=$< --output-file=$@ --locale=$(patsubst $(LOCALE_DIR)/%/LC_MESSAGES/$(DOMAIN).po,%,$@) --no-translator
endef

define update-po
	echo '  MSGMERGE  ' $@
	msgmerge --quiet --update --sort-by-file $@ $<
endef

define compile-po
	echo ' COMPILE-PO ' $<
	bin/pybabel --quiet compile --domain=$(DOMAIN) --input-file=$< --output-file=$@
endef

.PHONY: all clean
all: $(MO_FILES)
clean:
	$(RM) $(MO_FILES)

$(POT_FILE):
	$@(create-pot)

$(PO_FILES): $(POT_FILE)
	@[ -e $@ ] || $(create-po)
	@[ -e $@ ] && $(update-po)

%.mo: %.po
	@$(compile-po)
