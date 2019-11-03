'''Using django-tenants
Creating a Tenant
Creating a tenant works just like any other model in django. The first thing we should do is to create the public
tenant to make our main website available. We’ll use the previous model we defined for Client.
https://django-tenants.readthedocs.io/en/latest/use.html
'''

from customers.models import Customer, Domain

# create your public tenant
tenant = Customer(schema_name='public',
                username='public_tenant',
                first_name='public_firstname',
                last_name='public_last_name',
                email='public@email.com',
                phone='0000000000',
                )
tenant.save()

# Add one or more domains for the tenant
domain = Domain()
domain.domain = 'localhost' # don't add your port or www here! on a local server you'll want to use localhost here
domain.tenant = tenant
domain.is_primary = True
domain.save()

