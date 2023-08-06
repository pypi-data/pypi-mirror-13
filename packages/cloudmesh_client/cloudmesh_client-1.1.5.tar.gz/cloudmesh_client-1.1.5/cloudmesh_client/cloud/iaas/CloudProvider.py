from cloudmesh_client.common.ConfigDict import ConfigDict
from cloudmesh_client.cloud.iaas.provider.openstack.CloudProviderOpenstackAPI import \
    CloudProviderOpenstackAPI
from cloudmesh_client.cloud.iaas.CloudProviderBase import CloudProviderBase
import requests
from cloudmesh_client.common.Error import Error
from cloudmesh_client.common.todo import TODO

requests.packages.urllib3.disable_warnings()


class CloudProvider(CloudProviderBase):
    def __init__(self, cloudname, user=None, flat=True):
        super(CloudProvider, self).__init__(cloudname, user=user)


        try:
            d = ConfigDict("cloudmesh.yaml")
            if not cloudname in d["cloudmesh"]["clouds"]:
                raise ValueError("the cloud {} is not defined in the yaml file"
                                 .format(cloudname))

            cloud_details = d["cloudmesh"]["clouds"][cloudname]

            if cloud_details["cm_type"] == "openstack":
                provider = CloudProviderOpenstackAPI(
                    cloudname,
                    cloud_details,
                    flat=flat)
                self.provider = provider
                self.provider_class = CloudProviderOpenstackAPI

            if cloud_details["cm_type"] == "ec2":
                print("ec2 cloud provider yet to be implemented")
                TODO.implement()

            if cloud_details["cm_type"] == "azure":
                print("azure cloud provider yet to be implemented")
                TODO.implement()

        except Exception, e:
            Error.traceback(e)

    def get_attributes(self, kind):
        return self.provider.attributes(kind)



def main():
    from pprint import pprint

    cloud = "kilo"
    provider = CloudProvider(cloud).provider

    print (provider, type(provider))

    # pprint (provider.__dict__)
    # pprint (dir(provider))

    r = provider.list_flavor(cloud)
    pprint(r)

    for kind in ["flavor", "image", "vm", "limits", "quota"]:
        r = provider.list(kind, cloud)
        pprint(r)


if __name__ == "__main__":
    main()
