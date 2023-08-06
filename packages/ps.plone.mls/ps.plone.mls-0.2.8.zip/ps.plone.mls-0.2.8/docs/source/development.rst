Embedding Development Projects
==============================

Enable the Embedding for Development Projects
---------------------------------------------

To show development projects within your site, go to the place in your Plone site where you want to have the development projects available and open the **Actions**-menu.
Select **Activate Development Collection** from the available options:

.. image:: ../_images/activate_development_collection.png

When the **Development Collection** was activated, you will see a status message:

.. image:: ../_images/activate_development_collection_done.png

This will by default show you all available development projects from your connected MLS.
To change the settings for this embedding, click on the link **Configure Development Collection**.

The configuration is split into two parts:

- Basic Settings (define the representation of the developments)
- Filter Options (set pre-defined search criterias)

Basic Settings
##############

With the basic settings, available under the **Default** tab, you can adjust the visual representations of the developments:

.. image:: ../_images/configure_development_collection.png

Zoom level for maps
    This is the default level of detail for the maps within the community page of a development.
    You can choose a value between *0* and *21*, where *0* shows the entire world and *21* is at street level.
    Please note that not all zoom levels are available for all areas.

Show Contact Information
    Enable this setting to show the contact information for this development.
    If the **customized contact information** is enabled (either globally in the Plone site or locally for your embedding), the contact information will be updated or replaced based on those settings.

Show Contact Form
    Enable this setting to show a contact form within the community page of a development.
    When the contact form is submitted, an email will be sent to the responsible agent about that request.
    If the **customized contact information** is enabled (either globally in the Plone site or locally for your embedding), the email will be sent to the therein set email address of the responsible agent.

Show Captcha
    Enable this setting to show a spam preventing captcha within the contact form.

Developments per Page
    How many developments should be visible per page?
    If more developments are available, users can use the provided links to navigate through the search results.

Listings per Page
    How many listings should be visible per devlopment listings page?
    If more listings are available, users can use the provided links to navigate through the search results.

Filter Options
##############

To refine the search results for the develoments, use the options provided at the **Filter Options** tab:

.. image:: ../_images/configure_development_collection_filter.png

Agency Developments
    Enable this option to only show developments from the configured agency.

    .. note::
        This filter does not work if the agency ID set in the MLS configuration does not match the provided API key.

Searchable Text
    Use this option to search for developments.
    The information which is used for this search criterium is based on the following information of a development project:

    - **id**: The ID of the development, as shown in the URL of the browser address bar, like ``cayo-ranch``.
    - **title**: The name/title of the development, like ``Cayo Ranch``.
    - **description**: The short description (available in one or more languages).
    - **long_description**: The detailled description (available in one or more languages).
    - **area_description**: Information about the area (available in one or more languages).
    - **city**: Name of the city, like ``Puerto Cayo``.
    - **district**: Name of the local district (3rd administrative level), like ``Puerto De Cayo``.
    - **region**: Name of the county/region (2nd administrative level), like ``Jipijapa``.
    - **subdivision**: Name of the state/subdivision (1st administrative level), like ``Manabí``.
    - **country**: Name of the county, like ``Ecuador``.

    You can use **AND**, **OR** and **NOT** to build a more complex search query, e.g.::

        ecuador AND NOT quito AND luxury

    Summarizing the default operator rules:

    - A sequence of words without operators implies AND, e.g. ``casa beach``.
    - Double-quoted text implies phrase search, e.g. ``"casa beach"``.
    - Words connected by punctuation implies phrase search, e.g. ``casa-beach``.
    - A leading hyphen implies NOT, e.g. ``casa -beach``
    - These rules can be combined, e.g. ``casa -"casa beach"`` or ``casa -casa-beach``.
    - \* and ? are used for globbing (i.e. prefix search), e.g. ``casa*``.

Sort results by
    Sort the search results by the given sort option.
    The current available values are:

    - **No selection**: The results are sorted by relevance.
    - **Created**: The results are sorted by the date and time the developments were created.
    - **Title**: The results are sorted by the development title.

Reverse sort order?
    Enable this setting to reverse the sort order.

    .. note::
        To build e.g. a *Recent Developments* collection, where the newest developments will show up first, select **Created** from the **Sort results by** selection and enable the **Reverse sort order?** option.

Once all configuration options are entered click the **Save** button.


Disable the Embedding for Development Projects
----------------------------------------------

You can disable the embedding of development projects at any time.
When you deactivate the embedding, your configuration will not be removed.
So if you later decide to enable the embedding again, you don't have to start from the beginning.

To deactivate the **Development Collection**, open the **Actions**-menu and select **Deactivate Development Collection**:

.. image:: ../_images/deactivate_development_collection.png

When the **Development Collection** was deactivated, you will see a status message:

.. image:: ../_images/deactivate_development_collection_done.png

