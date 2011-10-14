#
# Makefile: automate the creation of the conpaas tarball
#

NAME=conpaas
VERSION:=0.1.0-$(shell date '+%s')


WDIR=work

INCLUDES=$(filter-out $(WDIR) map-reduce scalaris bag-of-tasks sql, $(wildcard *))

BIN_DIR=web-servers/scripts
BIN_CONF=$(addprefix $(BIN_DIR)/, ec2-manager-user-data opennebula-manager-user-data)
BIN_CODE=$(filter-out $(BIN_CONF), $(wildcard $(BIN_DIR)/*))
SDK_URL=http://pear.amazonwebservices.com/get/sdk-latest.zip

CODE_DIR=frontend/www/code
CONF_DIR=frontend/www/conf
SDK_DIR=frontend/www/lib/aws-sdk



help:
	@echo "Usage: make package [VERSION=<version>]"


$(WDIR):
	mkdir -p $(WDIR)

$(WDIR)/sdk-latest.zip:
	wget -P $(WDIR) $(SDK_URL)

package: $(WDIR) $(WDIR)/sdk-latest.zip
	mkdir -p $(WDIR)/$(CONF_DIR)
	install $(BIN_CONF) $(WDIR)/$(CONF_DIR)
	mkdir -p $(WDIR)/$(CODE_DIR)
	install -m 755 $(BIN_CODE) $(WDIR)/$(CODE_DIR)
	tar czf $(WDIR)/$(CODE_DIR)/ConPaaSWeb.tar.gz --exclude-vcs \
		--transform 's/^web-servers/ConPaaSWeb/' web-servers
	unzip -u -d $(WDIR) $(WDIR)/sdk-latest.zip
	mkdir -p $(WDIR)/$(SDK_DIR)
	cp -r $(WDIR)/sdk-*/sdk-*/* $(WDIR)/$(SDK_DIR)
	tar czf $(WDIR)/$(NAME)-$(VERSION).tar.gz --exclude-vcs \
		--transform 's|^$(WDIR)/||' \
		$(INCLUDES) $(WDIR)/frontend/


clean:
	rm -fr $(WDIR)

