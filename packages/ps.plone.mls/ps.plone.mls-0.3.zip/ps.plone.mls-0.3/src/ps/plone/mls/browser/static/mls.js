function resize_icons(icons){
  // adjust height & width to make the icons fit in one line
  icon_width = jQuery(icons[0]).width();
  // square the icon
  jQuery(icons).height(icon_width);
}

jQuery(function(jq) {

  if (jq('.mls .development__gallery .thumbnails').length > 0) {
    // Build JS Gallery for development detail view.

    // Load the theme ones more. This is necessary for mobile devices.
    Galleria.loadTheme('++resource++plone.mls.listing.javascript/classic/galleria.classic.min.js');
    jq('.mls .development__gallery .thumbnails').before('<div id="galleria" class="development__galleria"></div>');

    // Hide the thumbnails
    jq('.mls .development__gallery .thumbnails').hide();

    // Initialize Galleria.
    var galleria_obj = jq('#galleria').galleria({
      dataSource: '.thumbnails',
      width: 'auto',
      height: 400,
      preload: 3,
      transition: 'fade',
      transitionSpeed: 1000,
      autoplay: 5000
    });
  }

  if (jq('#content-views #contentview-featured-listings-config').length > 0) {
    // Show the featured listing configuration form with a nice overlay.
    jq('#content-views #contentview-featured-listings-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

  if (jq('#content-views #contentview-development-collection-config').length > 0) {
    // Show the development collection configuration form with a nice overlay.
    jq('#content-views #contentview-development-collection-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

});
