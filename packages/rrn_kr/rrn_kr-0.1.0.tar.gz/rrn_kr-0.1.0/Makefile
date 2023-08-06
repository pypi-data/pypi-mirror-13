POT_FILE=rrn_kr/locale/rrn_kr.pot
PO_FILES=\
	rrn_kr/locale/ko/LC_MESSAGES/rrn_kr.po
MO_FILES=\
	rrn_kr/locale/ko/LC_MESSAGES/rrn_kr.mo

all: $(MO_FILES)

$(POT_FILE):
	bin/pot-create -d rrn_kr --package-name rrn_kr --package-version 0.0.0 --msgid-bugs-address mete0r@sarangbang.or.kr --sort-by-file -o $@ rrn_kr

rrn_kr/locale/ko/LC_MESSAGES/rrn_kr.po: $(POT_FILE)
	if [ -e $@ ]; then \
		msgmerge --update --sort-by-file $@ $< ; \
	else \
		msginit -i $< -o $@ --locale ko; \
	fi

rrn_kr/locale/ko/LC_MESSAGES/rrn_kr.mo: rrn_kr/locale/ko/LC_MESSAGES/rrn_kr.po
	msgfmt -o $@ $<
