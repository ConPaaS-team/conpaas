SOURCE		=	.
PACKAGE_NAME	=	conpaas-sql.tar
DEST_DIR_PCKG	=	$(DIR)/$(PACKAGE_NAME)

install:
	# Creating destination directory if necessary
	mkdir -p $(DIR)
	# Copy directory structure to the destination directory.
	tar --exclude=".svn" -cvf $(DEST_DIR_PCKG) $(SOURCE)
	# Untar there
	tar xvf $(DEST_DIR_PCKG) -C $(DIR)
	# Remove the package
	rm $(DEST_DIR_PCKG)
	# Installation complete!
