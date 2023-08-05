from Products.CMFPlone.utils import getToolByName

PROFILE_ID = 'profile-collective.aaf:default'


def run_import_step(context, step):
    """ Re-import some specified import step for Generic Setup.
    """
    setup = getToolByName(context, 'portal_setup')
    return setup.runImportStepFromProfile(PROFILE_ID, step)


def upgrade_0001_to_0002(context):
    acl = getToolByName(context, 'acl_users')
    plugin = acl['AutoUserMakerPASPlugin']
    plugin.auto_update_user_properties = 1


def upgrade_all_to_0003(context):
    # Install new package
    qi = getToolByName(context, 'portal_quickinstaller')
    qi.installProduct('collective.shibboleth')

    # Remove old portlet config by importing profile
    setup = getToolByName(context, 'portal_setup')
    return setup.runImportStepFromProfile(
        'profile-collective.aaf:upgrade_portlet', 'portlets')
