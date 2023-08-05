# -*- encoding: utf-8 -*-
# Copyright (c) 2015 b<>com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

from oslo_log import log
from watcher_metering_vsphere.base import BaseVSphereMetricPuller

LOG = log.getLogger(__name__)


class VSphereHostClusterServicesCpufairnessLatest(BaseVSphereMetricPuller):
    """Fairness of distributed CPU resource allocation"""
    metric_group = "host"
    metric_name = "clusterServices.cpufairness.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostClusterServicesEffectivecpuAverage(BaseVSphereMetricPuller):
    """Total available CPU resources of all hosts within a cluster"""
    metric_group = "host"
    metric_name = "clusterServices.effectivecpu.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostClusterServicesEffectivememAverage(BaseVSphereMetricPuller):
    """Total amount of machine memory of all hosts in the cluster that is
    available for use for virtual machine memory and overhead memory
    """
    metric_group = "host"
    metric_name = "clusterServices.effectivemem.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostClusterServicesFailoverLatest(BaseVSphereMetricPuller):
    """vSphere HA number of failures that can be tolerated"""
    metric_group = "host"
    metric_name = "clusterServices.failover.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostClusterServicesMemfairnessLatest(BaseVSphereMetricPuller):
    """Aggregate available memory resources of all the hosts within a
    cluster
    """
    metric_group = "host"
    metric_name = "clusterServices.memfairness.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostCpuCapacityContentionAverage(BaseVSphereMetricPuller):
    """Percent of time the VM is unable to run because it is contending for
    access to the physical CPU(s)
    """
    metric_group = "host"
    metric_name = "cpu.capacity.contention.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuCapacityDemandAverage(BaseVSphereMetricPuller):
    """The amount of CPU resources a VM would use if there were no CPU
    contention or CPU limit
    """
    metric_group = "host"
    metric_name = "cpu.capacity.demand.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuCapacityEntitlementAverage(BaseVSphereMetricPuller):
    """CPU resources devoted by the ESXi scheduler to the virtual machines and
    resource pools
    """
    metric_group = "host"
    metric_name = "cpu.capacity.entitlement.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuCapacityProvisionedAverage(BaseVSphereMetricPuller):
    """Capacity in MHz of the physical CPU cores"""
    metric_group = "host"
    metric_name = "cpu.capacity.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuCapacityUsageAverage(BaseVSphereMetricPuller):
    """CPU usage as a percent during the interval."""
    metric_group = "host"
    metric_name = "cpu.capacity.usage.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuCoreUtilization(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "host"
    metric_name = "cpu.coreUtilization"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuCoreUtilizationAverage(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "host"
    metric_name = "cpu.coreUtilization.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuCoreUtilizationMaximum(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "host"
    metric_name = "cpu.coreUtilization.maximum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuCoreUtilizationMinimum(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "host"
    metric_name = "cpu.coreUtilization.minimum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuCorecountContentionAverage(BaseVSphereMetricPuller):
    """Time the VM vCPU is ready to run, but is unable to run due to
    co-scheduling constraints
    """
    metric_group = "host"
    metric_name = "cpu.corecount.contention.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuCorecountProvisionedAverage(BaseVSphereMetricPuller):
    """The number of virtual processors provisioned to the entity."""
    metric_group = "host"
    metric_name = "cpu.corecount.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostCpuCorecountUsageAverage(BaseVSphereMetricPuller):
    """The number of virtual processors running on the host."""
    metric_group = "host"
    metric_name = "cpu.corecount.usage.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostCpuCostopSummation(BaseVSphereMetricPuller):
    """Time the virtual machine is ready to run, but is unable to run due to
    co-scheduling constraints
    """
    metric_group = "host"
    metric_name = "cpu.costop.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuCpuentitlementLatest(BaseVSphereMetricPuller):
    """Amount of CPU resources allocated to the virtual machine or resource
    pool, based on the total cluster capacity and the resource configuration
    of the resource hierarchy
    """
    metric_group = "host"
    metric_name = "cpu.cpuentitlement.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuDemandAverage(BaseVSphereMetricPuller):
    """The amount of CPU resources a virtual machine would use if there were
    no CPU contention or CPU limit
    """
    metric_group = "host"
    metric_name = "cpu.demand.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuDemandEntitlementRatioLatest(BaseVSphereMetricPuller):
    """CPU resource entitlement to CPU demand ratio (in percents)"""
    metric_group = "host"
    metric_name = "cpu.demandEntitlementRatio.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuEntitlementLatest(BaseVSphereMetricPuller):
    """CPU resources devoted by the ESX scheduler"""
    metric_group = "host"
    metric_name = "cpu.entitlement.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuIdleSummation(BaseVSphereMetricPuller):
    """Total time that the CPU spent in an idle state"""
    metric_group = "host"
    metric_name = "cpu.idle.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuLatencyAverage(BaseVSphereMetricPuller):
    """Percent of time the virtual machine is unable to run because it is
    contending for access to the physical CPU(s)
    """
    metric_group = "host"
    metric_name = "cpu.latency.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuMaxlimitedSummation(BaseVSphereMetricPuller):
    """Time the virtual machine is ready to run, but is not run due to maxing
    out its CPU limit setting
    """
    metric_group = "host"
    metric_name = "cpu.maxlimited.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuOverlapSummation(BaseVSphereMetricPuller):
    """Time the virtual machine was interrupted to perform system services on
    behalf of itself or other virtual machines
    """
    metric_group = "host"
    metric_name = "cpu.overlap.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuReadinessAverage(BaseVSphereMetricPuller):
    """Percentage of time that the virtual machine was ready, but could not
    get scheduled to run on the physical CPU
    """
    metric_group = "host"
    metric_name = "cpu.readiness.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuReadySummation(BaseVSphereMetricPuller):
    """Time that the virtual machine was ready, but could not get scheduled to
    run on the physical CPU during last measurement interval
    """
    metric_group = "host"
    metric_name = "cpu.ready.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuReservedCapacityAverage(BaseVSphereMetricPuller):
    """Total CPU capacity reserved by virtual machines"""
    metric_group = "host"
    metric_name = "cpu.reservedCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuRunSummation(BaseVSphereMetricPuller):
    """Time the virtual machine is scheduled to run"""
    metric_group = "host"
    metric_name = "cpu.run.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuSwapwaitSummation(BaseVSphereMetricPuller):
    """CPU time spent waiting for swap-in"""
    metric_group = "host"
    metric_name = "cpu.swapwait.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuSystemSummation(BaseVSphereMetricPuller):
    """Amount of time spent on system processes on each virtual CPU in the
    virtual machine
    """
    metric_group = "host"
    metric_name = "cpu.system.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuTotalCapacityAverage(BaseVSphereMetricPuller):
    """Total CPU capacity reserved by and available for virtual machines"""
    metric_group = "host"
    metric_name = "cpu.totalCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuTotalmhzAverage(BaseVSphereMetricPuller):
    """Total amount of CPU resources of all hosts in the cluster"""
    metric_group = "host"
    metric_name = "cpu.totalmhz.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuUsage(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "host"
    metric_name = "cpu.usage"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUsageAverage(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "host"
    metric_name = "cpu.usage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUsageMaximum(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "host"
    metric_name = "cpu.usage.maximum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUsageMinimum(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "host"
    metric_name = "cpu.usage.minimum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUsagemhz(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "host"
    metric_name = "cpu.usagemhz"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuUsagemhzAverage(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "host"
    metric_name = "cpu.usagemhz.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuUsagemhzMaximum(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "host"
    metric_name = "cpu.usagemhz.maximum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuUsagemhzMinimum(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "host"
    metric_name = "cpu.usagemhz.minimum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostCpuUsedSummation(BaseVSphereMetricPuller):
    """Total CPU usage"""
    metric_group = "host"
    metric_name = "cpu.used.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostCpuUtilization(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "host"
    metric_name = "cpu.utilization"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUtilizationAverage(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "host"
    metric_name = "cpu.utilization.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUtilizationMaximum(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "host"
    metric_name = "cpu.utilization.maximum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuUtilizationMinimum(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "host"
    metric_name = "cpu.utilization.minimum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostCpuWaitSummation(BaseVSphereMetricPuller):
    """Total CPU time spent in wait state"""
    metric_group = "host"
    metric_name = "cpu.wait.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDatastoreBusResetsSummation(BaseVSphereMetricPuller):
    """busResets"""
    metric_group = "host"
    metric_name = "datastore.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreCommandsAbortedSummation(BaseVSphereMetricPuller):
    """commandsAborted"""
    metric_group = "host"
    metric_name = "datastore.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreIopsAverage(BaseVSphereMetricPuller):
    """Storage I/O Control aggregated IOPS"""
    metric_group = "host"
    metric_name = "datastore.datastoreIops.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreMaxQueueDepthLatest(
        BaseVSphereMetricPuller):
    """Storage I/O Control datastore maximum queue depth"""
    metric_group = "host"
    metric_name = "datastore.datastoreMaxQueueDepth.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreNormalReadLatencyLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore normalized read latency"""
    metric_group = "host"
    metric_name = "datastore.datastoreNormalReadLatency.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreNormalWriteLatencyLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore normalized write latency"""
    metric_group = "host"
    metric_name = "datastore.datastoreNormalWriteLatency.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreReadBytesLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore bytes read"""
    metric_group = "host"
    metric_name = "datastore.datastoreReadBytes.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreReadIopsLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore read I/O rate"""
    metric_group = "host"
    metric_name = "datastore.datastoreReadIops.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreReadLoadMetricLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore metric for read workload model"""
    metric_group = "host"
    metric_name = "datastore.datastoreReadLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreReadOIOLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore outstanding read requests"""
    metric_group = "host"
    metric_name = "datastore.datastoreReadOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreVMObservedLatencyLatest(
        BaseVSphereMetricPuller):
    """The average datastore latency as seen by virtual machines"""
    metric_group = "host"
    metric_name = "datastore.datastoreVMObservedLatency.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreWriteBytesLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore bytes written"""
    metric_group = "host"
    metric_name = "datastore.datastoreWriteBytes.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreWriteIopsLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore write I/O rate"""
    metric_group = "host"
    metric_name = "datastore.datastoreWriteIops.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreWriteLoadMetricLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore metric for write workload model"""
    metric_group = "host"
    metric_name = "datastore.datastoreWriteLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreDatastoreWriteOIOLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore outstanding write requests"""
    metric_group = "host"
    metric_name = "datastore.datastoreWriteOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all datastores used by the host"""
    metric_group = "host"
    metric_name = "datastore.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDatastoreNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of read commands issued per second to the datastore
    during the collection interval
    """
    metric_group = "host"
    metric_name = "datastore.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreNumberWriteAveragedAverage(BaseVSphereMetricPuller):
    """Average number of write commands issued per second to the datastore
    during the collection interval
    """
    metric_group = "host"
    metric_name = "datastore.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDatastoreReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data from the datastore"""
    metric_group = "host"
    metric_name = "datastore.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDatastoreSiocActiveTimePercentageAverage(
        BaseVSphereMetricPuller):
    """Percentage of time Storage I/O Control actively controlled datastore
    latency
    """
    metric_group = "host"
    metric_name = "datastore.siocActiveTimePercentage.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostDatastoreSizeNormalizedDatastoreLatencyAverage(
        BaseVSphereMetricPuller):
    """Storage I/O Control size-normalized I/O latency"""
    metric_group = "host"
    metric_name = "datastore.sizeNormalizedDatastoreLatency.average"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereHostDatastoreThroughputContentionAverage(BaseVSphereMetricPuller):
    """contention"""
    metric_group = "host"
    metric_name = "datastore.throughput.contention.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDatastoreThroughputUsageAverage(BaseVSphereMetricPuller):
    """usage"""
    metric_group = "host"
    metric_name = "datastore.throughput.usage.average"
    metric_type = "cumulative"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDatastoreTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read from the datastore takes"""
    metric_group = "host"
    metric_name = "datastore.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDatastoreTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write to the datastore takes"""
    metric_group = "host"
    metric_name = "datastore.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDatastoreWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data to the datastore"""
    metric_group = "host"
    metric_name = "datastore.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskBusResetsSummation(BaseVSphereMetricPuller):
    """Number of SCSI-bus reset commands issued during the collection
    interval
    """
    metric_group = "host"
    metric_name = "disk.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskCapacityContentionAverage(BaseVSphereMetricPuller):
    """contention"""
    metric_group = "host"
    metric_name = "disk.capacity.contention.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostDiskCapacityLatest(BaseVSphereMetricPuller):
    """Configured size of the datastore"""
    metric_group = "host"
    metric_name = "disk.capacity.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskCapacityProvisionedAverage(BaseVSphereMetricPuller):
    """provisioned"""
    metric_group = "host"
    metric_name = "disk.capacity.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskCapacityUsageAverage(BaseVSphereMetricPuller):
    """usage"""
    metric_group = "host"
    metric_name = "disk.capacity.usage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskCommandsSummation(BaseVSphereMetricPuller):
    """Number of SCSI commands issued during the collection interval"""
    metric_group = "host"
    metric_name = "disk.commands.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskCommandsAbortedSummation(BaseVSphereMetricPuller):
    """Number of SCSI commands aborted during the collection interval"""
    metric_group = "host"
    metric_name = "disk.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskCommandsAveragedAverage(BaseVSphereMetricPuller):
    """Average number of SCSI commands issued per second during the collection
    interval
    """
    metric_group = "host"
    metric_name = "disk.commandsAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskDeltausedLatest(BaseVSphereMetricPuller):
    """Storage overhead of a virtual machine or a datastore due to delta disk
    backings
    """
    metric_group = "host"
    metric_name = "disk.deltaused.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskDeviceLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, to complete a SCSI command
    from the physical device
    """
    metric_group = "host"
    metric_name = "disk.deviceLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskDeviceReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, to read from the physical
    device
    """
    metric_group = "host"
    metric_name = "disk.deviceReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskDeviceWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, to write to the physical
    device
    """
    metric_group = "host"
    metric_name = "disk.deviceWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskKernelLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, spent by VMkernel to process
    each SCSI command
    """
    metric_group = "host"
    metric_name = "disk.kernelLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskKernelReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, spent by VMkernel to process
    each SCSI read command
    """
    metric_group = "host"
    metric_name = "disk.kernelReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskKernelWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, spent by VMkernel to process
    each SCSI write command
    """
    metric_group = "host"
    metric_name = "disk.kernelWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskMaxQueueDepthAverage(BaseVSphereMetricPuller):
    """Maximum queue depth"""
    metric_group = "host"
    metric_name = "disk.maxQueueDepth.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all disks used by the host"""
    metric_group = "host"
    metric_name = "disk.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskNumberReadSummation(BaseVSphereMetricPuller):
    """Number of disk reads during the collection interval"""
    metric_group = "host"
    metric_name = "disk.numberRead.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of disk reads per second during the collection
    interval
    """
    metric_group = "host"
    metric_name = "disk.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskNumberWriteSummation(BaseVSphereMetricPuller):
    """Number of disk writes during the collection interval"""
    metric_group = "host"
    metric_name = "disk.numberWrite.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskNumberWriteAveragedAverage(BaseVSphereMetricPuller):
    """Average number of disk writes per second during the collection
    interval
    """
    metric_group = "host"
    metric_name = "disk.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskProvisionedLatest(BaseVSphereMetricPuller):
    """Amount of storage set aside for use by a datastore or a virtual
    machine
    """
    metric_group = "host"
    metric_name = "disk.provisioned.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskQueueLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI command,
    during the collection interval
    """
    metric_group = "host"
    metric_name = "disk.queueLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskQueueReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI read
    command, during the collection interval
    """
    metric_group = "host"
    metric_name = "disk.queueReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskQueueWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI write
    command, during the collection interval
    """
    metric_group = "host"
    metric_name = "disk.queueWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskReadAverage(BaseVSphereMetricPuller):
    """Average number of kilobytes read from the disk each second during the
    collection interval
    """
    metric_group = "host"
    metric_name = "disk.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskScsiReservationCnflctsPctAverage(BaseVSphereMetricPuller):
    """Number of SCSI reservation conflicts for the LUN as a percent of total
    commands during the collection interval
    """
    metric_group = "host"
    metric_name = "disk.scsiReservationCnflctsPct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostDiskScsiReservationConflictsSummation(
        BaseVSphereMetricPuller):
    """Number of SCSI reservation conflicts for the LUN during the collection
    interval
    """
    metric_group = "host"
    metric_name = "disk.scsiReservationConflicts.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostDiskThroughputContentionAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "host"
    metric_name = "disk.throughput.contention.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskThroughputUsageAverage(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate, including the rates for all virtual machines
    running on the host during the collection interval
    """
    metric_group = "host"
    metric_name = "disk.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskTotalLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time taken during the collection interval to process
    a SCSI command issued by the guest OS to the virtual machine
    """
    metric_group = "host"
    metric_name = "disk.totalLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time taken during the collection interval to process
    a SCSI read command issued from the guest OS to the virtual machine
    """
    metric_group = "host"
    metric_name = "disk.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time taken during the collection interval to process
    a SCSI write command issued by the guest OS to the virtual machine
    """
    metric_group = "host"
    metric_name = "disk.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostDiskUnsharedLatest(BaseVSphereMetricPuller):
    """Amount of space associated exclusively with a virtual machine"""
    metric_group = "host"
    metric_name = "disk.unshared.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskUsage(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "host"
    metric_name = "disk.usage"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskUsageAverage(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "host"
    metric_name = "disk.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskUsageMaximum(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "host"
    metric_name = "disk.usage.maximum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskUsageMinimum(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "host"
    metric_name = "disk.usage.minimum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostDiskUsedLatest(BaseVSphereMetricPuller):
    """Amount of space actually used by the virtual machine or the datastore"""
    metric_group = "host"
    metric_name = "disk.used.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostDiskWriteAverage(BaseVSphereMetricPuller):
    """Average number of kilobytes written to disk each second during the
    collection interval
    """
    metric_group = "host"
    metric_name = "disk.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostHbrHbrNetRxAverage(BaseVSphereMetricPuller):
    """Average amount of data received per second"""
    metric_group = "host"
    metric_name = "hbr.hbrNetRx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostHbrHbrNetTxAverage(BaseVSphereMetricPuller):
    """Average amount of data transmitted per second"""
    metric_group = "host"
    metric_name = "hbr.hbrNetTx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostHbrHbrNumVmsAverage(BaseVSphereMetricPuller):
    """Current number of replicated virtual machines"""
    metric_group = "host"
    metric_name = "hbr.hbrNumVms.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostManagementAgentCpuUsageAverage(BaseVSphereMetricPuller):
    """Amount of Service Console CPU usage"""
    metric_group = "host"
    metric_name = "managementAgent.cpuUsage.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostManagementAgentMemUsedAverage(BaseVSphereMetricPuller):
    """Amount of total configured memory that is available for use"""
    metric_group = "host"
    metric_name = "managementAgent.memUsed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostManagementAgentSwapInAverage(BaseVSphereMetricPuller):
    """Amount of memory that is swapped in for the Service Console"""
    metric_group = "host"
    metric_name = "managementAgent.swapIn.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostManagementAgentSwapOutAverage(BaseVSphereMetricPuller):
    """Amount of memory that is swapped out for the Service Console"""
    metric_group = "host"
    metric_name = "managementAgent.swapOut.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostManagementAgentSwapUsedAverage(BaseVSphereMetricPuller):
    """Sum of the memory swapped by all powered-on virtual machines on the
    host
    """
    metric_group = "host"
    metric_name = "managementAgent.swapUsed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemActive(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "host"
    metric_name = "mem.active"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemActiveAverage(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "host"
    metric_name = "mem.active.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemActiveMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "host"
    metric_name = "mem.active.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemActiveMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "host"
    metric_name = "mem.active.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemActivewriteAverage(BaseVSphereMetricPuller):
    """Estimate for the amount of memory actively being written to by the
    virtual machine
    """
    metric_group = "host"
    metric_name = "mem.activewrite.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityContentionAverage(BaseVSphereMetricPuller):
    """Percentage of time VMs are waiting to access swapped, compressed or
    ballooned memory
    """
    metric_group = "host"
    metric_name = "mem.capacity.contention.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemCapacityEntitlementAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory the VM is entitled to, as determined by
    the ESXi scheduler
    """
    metric_group = "host"
    metric_name = "mem.capacity.entitlement.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityProvisionedAverage(BaseVSphereMetricPuller):
    """Total amount of memory available to the host"""
    metric_group = "host"
    metric_name = "mem.capacity.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityUsableAverage(BaseVSphereMetricPuller):
    """Amount of physical memory available for use by virtual machines on this
    host
    """
    metric_group = "host"
    metric_name = "mem.capacity.usable.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityUsageAverage(BaseVSphereMetricPuller):
    """Amount of physical memory actively used"""
    metric_group = "host"
    metric_name = "mem.capacity.usage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityUsageUserworldAverage(BaseVSphereMetricPuller):
    """userworld"""
    metric_group = "host"
    metric_name = "mem.capacity.usage.userworld.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityUsageVmAverage(BaseVSphereMetricPuller):
    """vm"""
    metric_group = "host"
    metric_name = "mem.capacity.usage.vm.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityUsageVmOvrhdAverage(BaseVSphereMetricPuller):
    """vmOvrhd"""
    metric_group = "host"
    metric_name = "mem.capacity.usage.vmOvrhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCapacityUsageVmkOvrhdAverage(BaseVSphereMetricPuller):
    """vmkOvrhd"""
    metric_group = "host"
    metric_name = "mem.capacity.usage.vmkOvrhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCompressedAverage(BaseVSphereMetricPuller):
    """Amount of guest physical memory compressed by ESX/ESXi"""
    metric_group = "host"
    metric_name = "mem.compressed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemCompressionRateAverage(BaseVSphereMetricPuller):
    """Rate of memory compression for the virtual machine"""
    metric_group = "host"
    metric_name = "mem.compressionRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostMemConsumed(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "host"
    metric_name = "mem.consumed"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemConsumedAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "host"
    metric_name = "mem.consumed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemConsumedMaximum(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "host"
    metric_name = "mem.consumed.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemConsumedMinimum(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "host"
    metric_name = "mem.consumed.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemConsumedUserworldsAverage(BaseVSphereMetricPuller):
    """Amount of physical memory consumed by userworlds on this host"""
    metric_group = "host"
    metric_name = "mem.consumed.userworlds.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemConsumedVmsAverage(BaseVSphereMetricPuller):
    """Amount of physical memory consumed by VMs on this host"""
    metric_group = "host"
    metric_name = "mem.consumed.vms.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemDecompressionRateAverage(BaseVSphereMetricPuller):
    """Rate of memory decompression for the virtual machine"""
    metric_group = "host"
    metric_name = "mem.decompressionRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostMemEntitlementAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory the virtual machine is entitled to, as
    determined by the ESX scheduler
    """
    metric_group = "host"
    metric_name = "mem.entitlement.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemGranted(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "host"
    metric_name = "mem.granted"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemGrantedAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "host"
    metric_name = "mem.granted.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemGrantedMaximum(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "host"
    metric_name = "mem.granted.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemGrantedMinimum(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "host"
    metric_name = "mem.granted.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeap(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "host"
    metric_name = "mem.heap"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapAverage(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "host"
    metric_name = "mem.heap.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapMaximum(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "host"
    metric_name = "mem.heap.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapMinimum(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "host"
    metric_name = "mem.heap.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapfree(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "host"
    metric_name = "mem.heapfree"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapfreeAverage(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "host"
    metric_name = "mem.heapfree.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapfreeMaximum(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "host"
    metric_name = "mem.heapfree.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemHeapfreeMinimum(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "host"
    metric_name = "mem.heapfree.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLatencyAverage(BaseVSphereMetricPuller):
    """Percentage of time the virtual machine is waiting to access swapped or
    compressed memory
    """
    metric_group = "host"
    metric_name = "mem.latency.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemLlSwapIn(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapIn"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapInAverage(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapIn.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapInMaximum(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapIn.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapInMinimum(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapIn.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapInRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is being swapped from host cache into active
    memory
    """
    metric_group = "host"
    metric_name = "mem.llSwapInRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostMemLlSwapOut(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapOut"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapOutAverage(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapOut.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapOutMaximum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapOut.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapOutMinimum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapOut.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapOutRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is being swapped from active memory to host
    cache
    """
    metric_group = "host"
    metric_name = "mem.llSwapOutRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostMemLlSwapUsed(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapUsed"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapUsedAverage(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapUsed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapUsedMaximum(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapUsed.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLlSwapUsedMinimum(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "host"
    metric_name = "mem.llSwapUsed.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemLowfreethresholdAverage(BaseVSphereMetricPuller):
    """Threshold of free host physical memory below which ESX/ESXi will begin
    reclaiming memory from virtual machines through ballooning and swapping
    """
    metric_group = "host"
    metric_name = "mem.lowfreethreshold.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemMementitlementLatest(BaseVSphereMetricPuller):
    """Memory allocation as calculated by the VMkernel scheduler based on
    current estimated demand and reservation, limit, and shares policies set
    for all virtual machines and resource pools in the host or cluster
    """
    metric_group = "host"
    metric_name = "mem.mementitlement.latest"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostMemOverhead(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "host"
    metric_name = "mem.overhead"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemOverheadAverage(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "host"
    metric_name = "mem.overhead.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemOverheadMaximum(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "host"
    metric_name = "mem.overhead.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemOverheadMinimum(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "host"
    metric_name = "mem.overhead.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemOverheadMaxAverage(BaseVSphereMetricPuller):
    """Host physical memory (KB) reserved for use as the virtualization
    overhead for the virtual machine
    """
    metric_group = "host"
    metric_name = "mem.overheadMax.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemOverheadTouchedAverage(BaseVSphereMetricPuller):
    """Actively touched overhead host physical memory (KB) reserved for use as
    the virtualization overhead for the virtual machine
    """
    metric_group = "host"
    metric_name = "mem.overheadTouched.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemReservedCapacityAverage(BaseVSphereMetricPuller):
    """Total amount of memory reservation used by powered-on virtual machines
    and vSphere services on the host
    """
    metric_group = "host"
    metric_name = "mem.reservedCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostMemReservedCapacityUserworldAverage(BaseVSphereMetricPuller):
    """userworld"""
    metric_group = "host"
    metric_name = "mem.reservedCapacity.userworld.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemReservedCapacityVmAverage(BaseVSphereMetricPuller):
    """vm"""
    metric_group = "host"
    metric_name = "mem.reservedCapacity.vm.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemReservedCapacityVmOvhdAverage(BaseVSphereMetricPuller):
    """vmOvhd"""
    metric_group = "host"
    metric_name = "mem.reservedCapacity.vmOvhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemReservedCapacityVmkOvrhdAverage(BaseVSphereMetricPuller):
    """vmkOvrhd"""
    metric_group = "host"
    metric_name = "mem.reservedCapacity.vmkOvrhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemReservedCapacityPctAverage(BaseVSphereMetricPuller):
    """Percent of memory that has been reserved either through VMkernel use,
    by userworlds or due to VM memory reservations
    """
    metric_group = "host"
    metric_name = "mem.reservedCapacityPct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemShared(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "host"
    metric_name = "mem.shared"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedAverage(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "host"
    metric_name = "mem.shared.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedMaximum(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "host"
    metric_name = "mem.shared.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedMinimum(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "host"
    metric_name = "mem.shared.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedcommon(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "host"
    metric_name = "mem.sharedcommon"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedcommonAverage(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "host"
    metric_name = "mem.sharedcommon.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedcommonMaximum(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "host"
    metric_name = "mem.sharedcommon.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSharedcommonMinimum(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "host"
    metric_name = "mem.sharedcommon.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemStateLatest(BaseVSphereMetricPuller):
    """One of four threshold levels representing the percentage of free memory
    on the host. The counter value determines swapping and ballooning behavior
    for memory reclamation.
    """
    metric_group = "host"
    metric_name = "mem.state.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostMemSwapIn(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "host"
    metric_name = "mem.swapIn"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapInAverage(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "host"
    metric_name = "mem.swapIn.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapInMaximum(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "host"
    metric_name = "mem.swapIn.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapInMinimum(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "host"
    metric_name = "mem.swapIn.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapOut(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "host"
    metric_name = "mem.swapOut"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapOutAverage(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "host"
    metric_name = "mem.swapOut.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapOutMaximum(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "host"
    metric_name = "mem.swapOut.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapOutMinimum(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "host"
    metric_name = "mem.swapOut.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapin(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "host"
    metric_name = "mem.swapin"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapinAverage(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "host"
    metric_name = "mem.swapin.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapinMaximum(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "host"
    metric_name = "mem.swapin.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapinMinimum(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "host"
    metric_name = "mem.swapin.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapinRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is swapped from disk into active memory during the
    interval
    """
    metric_group = "host"
    metric_name = "mem.swapinRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostMemSwapout(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "host"
    metric_name = "mem.swapout"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapoutAverage(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "host"
    metric_name = "mem.swapout.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapoutMaximum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "host"
    metric_name = "mem.swapout.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapoutMinimum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "host"
    metric_name = "mem.swapout.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapoutRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is being swapped from active memory to disk during
    the current interval
    """
    metric_group = "host"
    metric_name = "mem.swapoutRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostMemSwapped(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "host"
    metric_name = "mem.swapped"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwappedAverage(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "host"
    metric_name = "mem.swapped.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwappedMaximum(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "host"
    metric_name = "mem.swapped.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwappedMinimum(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "host"
    metric_name = "mem.swapped.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwaptarget(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "host"
    metric_name = "mem.swaptarget"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwaptargetAverage(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "host"
    metric_name = "mem.swaptarget.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwaptargetMaximum(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "host"
    metric_name = "mem.swaptarget.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwaptargetMinimum(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "host"
    metric_name = "mem.swaptarget.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapunreserved(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "host"
    metric_name = "mem.swapunreserved"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapunreservedAverage(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "host"
    metric_name = "mem.swapunreserved.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapunreservedMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "host"
    metric_name = "mem.swapunreserved.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapunreservedMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "host"
    metric_name = "mem.swapunreserved.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapused(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "host"
    metric_name = "mem.swapused"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapusedAverage(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "host"
    metric_name = "mem.swapused.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapusedMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "host"
    metric_name = "mem.swapused.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSwapusedMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "host"
    metric_name = "mem.swapused.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSysUsage(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "host"
    metric_name = "mem.sysUsage"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSysUsageAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "host"
    metric_name = "mem.sysUsage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSysUsageMaximum(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "host"
    metric_name = "mem.sysUsage.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemSysUsageMinimum(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "host"
    metric_name = "mem.sysUsage.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemTotalCapacityAverage(BaseVSphereMetricPuller):
    """Total amount of memory reservation used by and available for powered-on
    virtual machines and vSphere services on the host
    """
    metric_group = "host"
    metric_name = "mem.totalCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostMemTotalmbAverage(BaseVSphereMetricPuller):
    """Total amount of host physical memory of all hosts in the cluster that
    is available for virtual machine memory (physical memory for use by the
    guest OS) and virtual machine overhead memory
    """
    metric_group = "host"
    metric_name = "mem.totalmb.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostMemUnreserved(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "host"
    metric_name = "mem.unreserved"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemUnreservedAverage(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "host"
    metric_name = "mem.unreserved.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemUnreservedMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "host"
    metric_name = "mem.unreserved.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemUnreservedMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "host"
    metric_name = "mem.unreserved.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemUsage(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "host"
    metric_name = "mem.usage"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemUsageAverage(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "host"
    metric_name = "mem.usage.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemUsageMaximum(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "host"
    metric_name = "mem.usage.maximum"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemUsageMinimum(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "host"
    metric_name = "mem.usage.minimum"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemVmfsPbcCapMissRatioLatest(BaseVSphereMetricPuller):
    """Trailing average of the ratio of capacity misses to compulsory misses
    for the VMFS PB Cache
    """
    metric_group = "host"
    metric_name = "mem.vmfs.pbc.capMissRatio.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostMemVmfsPbcOverheadLatest(BaseVSphereMetricPuller):
    """Amount of VMFS heap used by the VMFS PB Cache"""
    metric_group = "host"
    metric_name = "mem.vmfs.pbc.overhead.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmfsPbcSizeLatest(BaseVSphereMetricPuller):
    """Space used for holding VMFS Pointer Blocks in memory"""
    metric_group = "host"
    metric_name = "mem.vmfs.pbc.size.latest"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostMemVmfsPbcSizeMaxLatest(BaseVSphereMetricPuller):
    """Maximum size the VMFS Pointer Block Cache can grow to"""
    metric_group = "host"
    metric_name = "mem.vmfs.pbc.sizeMax.latest"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereHostMemVmfsPbcWorkingSetLatest(BaseVSphereMetricPuller):
    """Amount of file blocks whose addresses are cached in the VMFS PB Cache"""
    metric_group = "host"
    metric_name = "mem.vmfs.pbc.workingSet.latest"
    metric_type = "cumulative"
    metric_unit = "TB"
    pulling_interval = 10


class VSphereHostMemVmfsPbcWorkingSetMaxLatest(BaseVSphereMetricPuller):
    """Maximum amount of file blocks whose addresses are cached in the VMFS PB
    Cache
    """
    metric_group = "host"
    metric_name = "mem.vmfs.pbc.workingSetMax.latest"
    metric_type = "cumulative"
    metric_unit = "TB"
    pulling_interval = 10


class VSphereHostMemVmmemctl(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "host"
    metric_name = "mem.vmmemctl"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctlAverage(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "host"
    metric_name = "mem.vmmemctl.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctlMaximum(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "host"
    metric_name = "mem.vmmemctl.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctlMinimum(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "host"
    metric_name = "mem.vmmemctl.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctltarget(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "host"
    metric_name = "mem.vmmemctltarget"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctltargetAverage(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "host"
    metric_name = "mem.vmmemctltarget.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctltargetMaximum(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "host"
    metric_name = "mem.vmmemctltarget.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemVmmemctltargetMinimum(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "host"
    metric_name = "mem.vmmemctltarget.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemZero(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "host"
    metric_name = "mem.zero"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemZeroAverage(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "host"
    metric_name = "mem.zero.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemZeroMaximum(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "host"
    metric_name = "mem.zero.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemZeroMinimum(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "host"
    metric_name = "mem.zero.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemZipSavedLatest(BaseVSphereMetricPuller):
    """Memory (KB) saved due to memory zipping"""
    metric_group = "host"
    metric_name = "mem.zipSaved.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostMemZippedLatest(BaseVSphereMetricPuller):
    """Memory (KB) zipped"""
    metric_group = "host"
    metric_name = "mem.zipped.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostNetBroadcastRxSummation(BaseVSphereMetricPuller):
    """Number of broadcast packets received during the sampling interval"""
    metric_group = "host"
    metric_name = "net.broadcastRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetBroadcastTxSummation(BaseVSphereMetricPuller):
    """Number of broadcast packets transmitted during the sampling interval"""
    metric_group = "host"
    metric_name = "net.broadcastTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetBytesRxAverage(BaseVSphereMetricPuller):
    """Average amount of data received per second"""
    metric_group = "host"
    metric_name = "net.bytesRx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetBytesTxAverage(BaseVSphereMetricPuller):
    """Average amount of data transmitted per second"""
    metric_group = "host"
    metric_name = "net.bytesTx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetDroppedRxSummation(BaseVSphereMetricPuller):
    """Number of receives dropped"""
    metric_group = "host"
    metric_name = "net.droppedRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetDroppedTxSummation(BaseVSphereMetricPuller):
    """Number of transmits dropped"""
    metric_group = "host"
    metric_name = "net.droppedTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetErrorsRxSummation(BaseVSphereMetricPuller):
    """Number of packets with errors received during the sampling interval"""
    metric_group = "host"
    metric_name = "net.errorsRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetErrorsTxSummation(BaseVSphereMetricPuller):
    """Number of packets with errors transmitted during the sampling
    interval
    """
    metric_group = "host"
    metric_name = "net.errorsTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetMulticastRxSummation(BaseVSphereMetricPuller):
    """Number of multicast packets received during the sampling interval"""
    metric_group = "host"
    metric_name = "net.multicastRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetMulticastTxSummation(BaseVSphereMetricPuller):
    """Number of multicast packets transmitted during the sampling interval"""
    metric_group = "host"
    metric_name = "net.multicastTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetPacketsRxSummation(BaseVSphereMetricPuller):
    """Number of packets received during the interval"""
    metric_group = "host"
    metric_name = "net.packetsRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetPacketsTxSummation(BaseVSphereMetricPuller):
    """Number of packets transmitted during the interval"""
    metric_group = "host"
    metric_name = "net.packetsTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetReceivedAverage(BaseVSphereMetricPuller):
    """Average rate at which data was received during the interval"""
    metric_group = "host"
    metric_name = "net.received.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputContentionSummation(BaseVSphereMetricPuller):
    """The aggregate network droppped packets for the host"""
    metric_group = "host"
    metric_name = "net.throughput.contention.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputDroppedRxAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.droppedRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputDroppedTxAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.droppedTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPacketsPerSecAverage(BaseVSphereMetricPuller):
    """Average rate of packets received and transmitted per second"""
    metric_group = "host"
    metric_name = "net.throughput.packetsPerSec.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPktsRxAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this vDS"""
    metric_group = "host"
    metric_name = "net.throughput.pktsRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPktsRxBroadcastAverage(BaseVSphereMetricPuller):
    """The rate of received Broadcast packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.pktsRxBroadcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPktsRxMulticastAverage(BaseVSphereMetricPuller):
    """The rate of received Multicast packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.pktsRxMulticast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPktsTxAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.pktsTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPktsTxBroadcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Broadcast packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.pktsTxBroadcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputPktsTxMulticastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Multicast packets for this VDS"""
    metric_group = "host"
    metric_name = "net.throughput.pktsTxMulticast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputProvisionedAverage(BaseVSphereMetricPuller):
    """The maximum network bandwidth for the host"""
    metric_group = "host"
    metric_name = "net.throughput.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsableAverage(BaseVSphereMetricPuller):
    """The current available network bandwidth for the host"""
    metric_group = "host"
    metric_name = "net.throughput.usable.average"
    metric_type = "cumulative"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageAverage(BaseVSphereMetricPuller):
    """The current network bandwidth usage for the host"""
    metric_group = "host"
    metric_name = "net.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageFtAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for FT"""
    metric_group = "host"
    metric_name = "net.throughput.usage.ft.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageHbrAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for HBR"""
    metric_group = "host"
    metric_name = "net.throughput.usage.hbr.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageIscsiAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for iSCSI"""
    metric_group = "host"
    metric_name = "net.throughput.usage.iscsi.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageNfsAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for NFS"""
    metric_group = "host"
    metric_name = "net.throughput.usage.nfs.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageVmAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for VMs"""
    metric_group = "host"
    metric_name = "net.throughput.usage.vm.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputUsageVmotionAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for vMotion"""
    metric_group = "host"
    metric_name = "net.throughput.usage.vmotion.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpFoundAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that found matched ARP entry for this
    network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpFound.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpFoundSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that found matched ARP entry for this
    network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpFound.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpLKUPFullAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new ARP entry
    during translation phase for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpLKUPFull.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpLKUPFullSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new ARP entry
    during translation phase for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpLKUPFull.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpTimeoutAverage(BaseVSphereMetricPuller):
    """Count of arp queries that have been expired for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.arpTimeout.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpTimeoutSummation(BaseVSphereMetricPuller):
    """Count of arp queries that have been expired for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.arpTimeout.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpUnknownAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets whose matched arp entry is marked as
    unknown for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpUnknown.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpUnknownSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets whose matched arp entry is marked as
    unknown for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpUnknown.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpWaitAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets whose ARP requests have already been sent
    into queue for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpWait.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsArpWaitSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets whose ARP requests have already been sent
    into queue for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.arpWait.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsDroppedRxAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.droppedRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsDroppedTxAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.droppedTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagDropRxAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagDropRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagDropTxAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagDropTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagRxAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagRxBcastAverage(BaseVSphereMetricPuller):
    """The rate of received Broadcast packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagRxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagRxMcastAverage(BaseVSphereMetricPuller):
    """The rate of received multicast packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagRxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagTxAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagTxBcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Broadcast packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagTxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsLagTxMcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Multicast packets for this LAG"""
    metric_group = "host"
    metric_name = "net.throughput.vds.lagTxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsMacFloodAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that cannot find matched mapping entry for
    this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.macFlood.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsMacFloodSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that cannot find matched mapping entry for
    this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.macFlood.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsMacLKUPFullAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during translation phase for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.macLKUPFull.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsMacLKUPFullSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during translation phase for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.macLKUPFull.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsMacUPDTFullAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during learning phase for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.macUPDTFull.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsMacUPDTFullSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during learning phase for this network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.macUPDTFull.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsPktsRxAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.pktsRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsPktsRxBcastAverage(BaseVSphereMetricPuller):
    """The rate of received broadcast packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.pktsRxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsPktsRxMcastAverage(BaseVSphereMetricPuller):
    """The rate of received multicast packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.pktsRxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsPktsTxAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.pktsTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsPktsTxBcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted broadcast packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.pktsTxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsPktsTxMcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted multicast packets for this DVPort"""
    metric_group = "host"
    metric_name = "net.throughput.vds.pktsTxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsRxDestErrAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets with destination IP error for this
    network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.rxDestErr.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsRxDestErrSummation(BaseVSphereMetricPuller):
    """Count of dropped received packets with destination IP error for this
    network
    """
    metric_group = "host"
    metric_name = "net.throughput.vds.rxDestErr.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsRxDropAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.rxDrop.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsRxDropSummation(BaseVSphereMetricPuller):
    """Count of dropped received packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.rxDrop.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsRxTotalAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.rxTotal.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsRxTotalSummation(BaseVSphereMetricPuller):
    """The rate of received packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.rxTotal.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxCrsRouterAverage(BaseVSphereMetricPuller):
    """The rate of transmitted cross-router packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txCrsRouter.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxCrsRouterSummation(BaseVSphereMetricPuller):
    """The rate of transmitted cross-router packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txCrsRouter.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxDropAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txDrop.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxDropSummation(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txDrop.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxNoUnicastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted non-unicast packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txNoUnicast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxNoUnicastSummation(BaseVSphereMetricPuller):
    """The rate of transmitted non-unicast packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txNoUnicast.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxTotalAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txTotal.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetThroughputVdsTxTotalSummation(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this network"""
    metric_group = "host"
    metric_name = "net.throughput.vds.txTotal.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetTransmittedAverage(BaseVSphereMetricPuller):
    """Average rate at which data was transmitted during the interval"""
    metric_group = "host"
    metric_name = "net.transmitted.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetUnknownProtosSummation(BaseVSphereMetricPuller):
    """Number of frames with unknown protocol received during the sampling
    interval
    """
    metric_group = "host"
    metric_name = "net.unknownProtos.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostNetUsage(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "host"
    metric_name = "net.usage"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetUsageAverage(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "host"
    metric_name = "net.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetUsageMaximum(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "host"
    metric_name = "net.usage.maximum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostNetUsageMinimum(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "host"
    metric_name = "net.usage.minimum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostPowerCapacityUsableAverage(BaseVSphereMetricPuller):
    """Current maximum allowed power usage."""
    metric_group = "host"
    metric_name = "power.capacity.usable.average"
    metric_type = "cumulative"
    metric_unit = "W"
    pulling_interval = 10


class VSphereHostPowerCapacityUsageAverage(BaseVSphereMetricPuller):
    """Current power usage"""
    metric_group = "host"
    metric_name = "power.capacity.usage.average"
    metric_type = "cumulative"
    metric_unit = "W"
    pulling_interval = 10


class VSphereHostPowerCapacityUsagePctAverage(BaseVSphereMetricPuller):
    """Current power usage as a percentage of maximum allowed power."""
    metric_group = "host"
    metric_name = "power.capacity.usagePct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostPowerEnergySummation(BaseVSphereMetricPuller):
    """Total energy used since last stats reset"""
    metric_group = "host"
    metric_name = "power.energy.summation"
    metric_type = "delta"
    metric_unit = "J"
    pulling_interval = 10


class VSphereHostPowerPowerAverage(BaseVSphereMetricPuller):
    """Current power usage"""
    metric_group = "host"
    metric_name = "power.power.average"
    metric_type = "gauge"
    metric_unit = "W"
    pulling_interval = 10


class VSphereHostPowerPowerCapAverage(BaseVSphereMetricPuller):
    """Maximum allowed power usage"""
    metric_group = "host"
    metric_name = "power.powerCap.average"
    metric_type = "cumulative"
    metric_unit = "W"
    pulling_interval = 10


class VSphereHostRescpuActav1Latest(BaseVSphereMetricPuller):
    """CPU active average over 1 minute"""
    metric_group = "host"
    metric_name = "rescpu.actav1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuActav15Latest(BaseVSphereMetricPuller):
    """CPU active average over 15 minutes"""
    metric_group = "host"
    metric_name = "rescpu.actav15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuActav5Latest(BaseVSphereMetricPuller):
    """CPU active average over 5 minutes"""
    metric_group = "host"
    metric_name = "rescpu.actav5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuActpk1Latest(BaseVSphereMetricPuller):
    """CPU active peak over 1 minute"""
    metric_group = "host"
    metric_name = "rescpu.actpk1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuActpk15Latest(BaseVSphereMetricPuller):
    """CPU active peak over 15 minutes"""
    metric_group = "host"
    metric_name = "rescpu.actpk15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuActpk5Latest(BaseVSphereMetricPuller):
    """CPU active peak over 5 minutes"""
    metric_group = "host"
    metric_name = "rescpu.actpk5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuMaxLimited1Latest(BaseVSphereMetricPuller):
    """Amount of CPU resources over the limit that were refused, average over
    1 minute
    """
    metric_group = "host"
    metric_name = "rescpu.maxLimited1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuMaxLimited15Latest(BaseVSphereMetricPuller):
    """Amount of CPU resources over the limit that were refused, average over
    15 minutes
    """
    metric_group = "host"
    metric_name = "rescpu.maxLimited15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuMaxLimited5Latest(BaseVSphereMetricPuller):
    """Amount of CPU resources over the limit that were refused, average over
    5 minutes
    """
    metric_group = "host"
    metric_name = "rescpu.maxLimited5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuRunav1Latest(BaseVSphereMetricPuller):
    """CPU running average over 1 minute"""
    metric_group = "host"
    metric_name = "rescpu.runav1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuRunav15Latest(BaseVSphereMetricPuller):
    """CPU running average over 15 minutes"""
    metric_group = "host"
    metric_name = "rescpu.runav15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuRunav5Latest(BaseVSphereMetricPuller):
    """CPU running average over 5 minutes"""
    metric_group = "host"
    metric_name = "rescpu.runav5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuRunpk1Latest(BaseVSphereMetricPuller):
    """CPU running peak over 1 minute"""
    metric_group = "host"
    metric_name = "rescpu.runpk1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuRunpk15Latest(BaseVSphereMetricPuller):
    """CPU running peak over 15 minutes"""
    metric_group = "host"
    metric_name = "rescpu.runpk15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuRunpk5Latest(BaseVSphereMetricPuller):
    """CPU running peak over 5 minutes"""
    metric_group = "host"
    metric_name = "rescpu.runpk5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostRescpuSampleCountLatest(BaseVSphereMetricPuller):
    """Group CPU sample count"""
    metric_group = "host"
    metric_name = "rescpu.sampleCount.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostRescpuSamplePeriodLatest(BaseVSphereMetricPuller):
    """Group CPU sample period"""
    metric_group = "host"
    metric_name = "rescpu.samplePeriod.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStorageAdapterOIOsPctAverage(BaseVSphereMetricPuller):
    """The percent of I/Os that have been issued but have not yet completed"""
    metric_group = "host"
    metric_name = "storageAdapter.OIOsPct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostStorageAdapterCommandsAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of commands issued per second by the storage adapter
    during the collection interval
    """
    metric_group = "host"
    metric_name = "storageAdapter.commandsAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStorageAdapterMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all storage adapters used by the host"""
    metric_group = "host"
    metric_name = "storageAdapter.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStorageAdapterNumberReadAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of read commands issued per second by the storage
    adapter during the collection interval
    """
    metric_group = "host"
    metric_name = "storageAdapter.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStorageAdapterNumberWriteAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of write commands issued per second by the storage
    adapter during the collection interval
    """
    metric_group = "host"
    metric_name = "storageAdapter.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStorageAdapterOutstandingIOsAverage(BaseVSphereMetricPuller):
    """The number of I/Os that have been issued but have not yet completed"""
    metric_group = "host"
    metric_name = "storageAdapter.outstandingIOs.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStorageAdapterQueueDepthAverage(BaseVSphereMetricPuller):
    """The maximum number of I/Os that can be outstanding at a given time"""
    metric_group = "host"
    metric_name = "storageAdapter.queueDepth.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStorageAdapterQueueLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI command,
    during the collection interval
    """
    metric_group = "host"
    metric_name = "storageAdapter.queueLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStorageAdapterQueuedAverage(BaseVSphereMetricPuller):
    """The current number of I/Os that are waiting to be issued"""
    metric_group = "host"
    metric_name = "storageAdapter.queued.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStorageAdapterReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data by the storage adapter"""
    metric_group = "host"
    metric_name = "storageAdapter.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostStorageAdapterThroughputContAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "host"
    metric_name = "storageAdapter.throughput.cont.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStorageAdapterThroughputUsagAverage(BaseVSphereMetricPuller):
    """The storage adapter's I/O rate"""
    metric_group = "host"
    metric_name = "storageAdapter.throughput.usag.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostStorageAdapterTotalReadLatencyAverage(
        BaseVSphereMetricPuller):
    """The average time a read by the storage adapter takes"""
    metric_group = "host"
    metric_name = "storageAdapter.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStorageAdapterTotalWriteLatencyAverage(
        BaseVSphereMetricPuller):
    """The average time a write by the storage adapter takes"""
    metric_group = "host"
    metric_name = "storageAdapter.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStorageAdapterWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data by the storage adapter"""
    metric_group = "host"
    metric_name = "storageAdapter.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostStoragePathBusResetsSummation(BaseVSphereMetricPuller):
    """Number of SCSI-bus reset commands issued during the collection
    interval
    """
    metric_group = "host"
    metric_name = "storagePath.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStoragePathCommandsAbortedSummation(BaseVSphereMetricPuller):
    """Number of SCSI commands terminated during the collection interval"""
    metric_group = "host"
    metric_name = "storagePath.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStoragePathCommandsAveragedAverage(BaseVSphereMetricPuller):
    """Average number of commands issued per second on the storage path during
    the collection interval
    """
    metric_group = "host"
    metric_name = "storagePath.commandsAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStoragePathMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all storage paths used by the host"""
    metric_group = "host"
    metric_name = "storagePath.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStoragePathNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of read commands issued per second on the storage path
    during the collection interval
    """
    metric_group = "host"
    metric_name = "storagePath.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStoragePathNumberWriteAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of write commands issued per second on the storage path
    during the collection interval
    """
    metric_group = "host"
    metric_name = "storagePath.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostStoragePathReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data on the storage path"""
    metric_group = "host"
    metric_name = "storagePath.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostStoragePathThroughputContAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "host"
    metric_name = "storagePath.throughput.cont.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStoragePathThroughputUsageAverage(BaseVSphereMetricPuller):
    """Storage path I/O rate"""
    metric_group = "host"
    metric_name = "storagePath.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostStoragePathTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read issued on the storage path takes"""
    metric_group = "host"
    metric_name = "storagePath.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStoragePathTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write issued on the storage path takes"""
    metric_group = "host"
    metric_name = "storagePath.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostStoragePathWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data on the storage path"""
    metric_group = "host"
    metric_name = "storagePath.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostSysDiskUsageLatest(BaseVSphereMetricPuller):
    """Amount of disk space usage for each mount point"""
    metric_group = "host"
    metric_name = "sys.diskUsage.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysHeartbeatLatest(BaseVSphereMetricPuller):
    """Number of heartbeats issued per virtual machine during the interval"""
    metric_group = "host"
    metric_name = "sys.heartbeat.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostSysHeartbeatSummation(BaseVSphereMetricPuller):
    """Number of heartbeats issued per virtual machine during the interval"""
    metric_group = "host"
    metric_name = "sys.heartbeat.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostSysOsUptimeLatest(BaseVSphereMetricPuller):
    """Total time elapsed, in seconds, since last operating system boot-up"""
    metric_group = "host"
    metric_name = "sys.osUptime.latest"
    metric_type = "cumulative"
    metric_unit = "s"
    pulling_interval = 10


class VSphereHostSysResourceCpuAct1Latest(BaseVSphereMetricPuller):
    """CPU active average over 1 minute of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuAct1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysResourceCpuAct5Latest(BaseVSphereMetricPuller):
    """CPU active average over 5 minutes of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuAct5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysResourceCpuAllocMaxLatest(BaseVSphereMetricPuller):
    """CPU allocation limit (in MHz) of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuAllocMax.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostSysResourceCpuAllocMinLatest(BaseVSphereMetricPuller):
    """CPU allocation reservation (in MHz) of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuAllocMin.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostSysResourceCpuAllocSharesLatest(BaseVSphereMetricPuller):
    """CPU allocation shares of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuAllocShares.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostSysResourceCpuMaxLimited1Latest(BaseVSphereMetricPuller):
    """CPU maximum limited over 1 minute of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuMaxLimited1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysResourceCpuMaxLimited5Latest(BaseVSphereMetricPuller):
    """CPU maximum limited over 5 minutes of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuMaxLimited5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysResourceCpuRun1Latest(BaseVSphereMetricPuller):
    """CPU running average over 1 minute of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuRun1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysResourceCpuRun5Latest(BaseVSphereMetricPuller):
    """CPU running average over 5 minutes of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceCpuRun5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostSysResourceCpuUsage(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "host"
    metric_name = "sys.resourceCpuUsage"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostSysResourceCpuUsageAverage(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "host"
    metric_name = "sys.resourceCpuUsage.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostSysResourceCpuUsageMaximum(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "host"
    metric_name = "sys.resourceCpuUsage.maximum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostSysResourceCpuUsageMinimum(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "host"
    metric_name = "sys.resourceCpuUsage.minimum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereHostSysResourceFdUsageLatest(BaseVSphereMetricPuller):
    """Number of file descriptors used by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceFdUsage.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostSysResourceMemAllocMaxLatest(BaseVSphereMetricPuller):
    """Memory allocation limit (in KB) of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemAllocMax.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemAllocMinLatest(BaseVSphereMetricPuller):
    """Memory allocation reservation (in KB) of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemAllocMin.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemAllocSharesLatest(BaseVSphereMetricPuller):
    """Memory allocation shares of the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemAllocShares.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostSysResourceMemConsumedLatest(BaseVSphereMetricPuller):
    """Memory consumed by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemConsumed.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemCowLatest(BaseVSphereMetricPuller):
    """Memory shared by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemCow.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemMappedLatest(BaseVSphereMetricPuller):
    """Memory mapped by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemMapped.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemOverheadLatest(BaseVSphereMetricPuller):
    """Overhead memory consumed by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemOverhead.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemSharedLatest(BaseVSphereMetricPuller):
    """Memory saved due to sharing by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemShared.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemSwappedLatest(BaseVSphereMetricPuller):
    """Memory swapped out by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemSwapped.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemTouchedLatest(BaseVSphereMetricPuller):
    """Memory touched by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemTouched.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysResourceMemZeroLatest(BaseVSphereMetricPuller):
    """Zero filled memory used by the system resource group"""
    metric_group = "host"
    metric_name = "sys.resourceMemZero.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostSysUptimeLatest(BaseVSphereMetricPuller):
    """Total time elapsed, in seconds, since last system startup"""
    metric_group = "host"
    metric_name = "sys.uptime.latest"
    metric_type = "cumulative"
    metric_unit = "s"
    pulling_interval = 10


class VSphereHostVcDebugInfoActivationlatencystatsMaximum(
        BaseVSphereMetricPuller):
    """The latency of an activation operation in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.activationlatencystats.maximum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVcDebugInfoActivationlatencystatsMinimum(
        BaseVSphereMetricPuller):
    """The latency of an activation operation in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.activationlatencystats.minimum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVcDebugInfoActivationlatencystatsSummation(
        BaseVSphereMetricPuller):
    """The latency of an activation operation in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.activationlatencystats.summation"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVcDebugInfoActivationstatsMaximum(BaseVSphereMetricPuller):
    """Activation operations in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.activationstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoActivationstatsMinimum(BaseVSphereMetricPuller):
    """Activation operations in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.activationstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoActivationstatsSummation(BaseVSphereMetricPuller):
    """Activation operations in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.activationstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoHostsynclatencystatsMaximum(
        BaseVSphereMetricPuller):
    """The latency of a host sync operation in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.hostsynclatencystats.maximum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVcDebugInfoHostsynclatencystatsMinimum(
        BaseVSphereMetricPuller):
    """The latency of a host sync operation in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.hostsynclatencystats.minimum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVcDebugInfoHostsynclatencystatsSummation(
        BaseVSphereMetricPuller):
    """The latency of a host sync operation in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.hostsynclatencystats.summation"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVcDebugInfoHostsyncstatsMaximum(BaseVSphereMetricPuller):
    """The number of host sync operations in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.hostsyncstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoHostsyncstatsMinimum(BaseVSphereMetricPuller):
    """The number of host sync operations in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.hostsyncstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoHostsyncstatsSummation(BaseVSphereMetricPuller):
    """The number of host sync operations in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.hostsyncstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoInventorystatsMaximum(BaseVSphereMetricPuller):
    """vCenter Server inventory statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.inventorystats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoInventorystatsMinimum(BaseVSphereMetricPuller):
    """vCenter Server inventory statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.inventorystats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoInventorystatsSummation(BaseVSphereMetricPuller):
    """vCenter Server inventory statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.inventorystats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoLockstatsMaximum(BaseVSphereMetricPuller):
    """vCenter Server locking statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.lockstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoLockstatsMinimum(BaseVSphereMetricPuller):
    """vCenter Server locking statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.lockstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoLockstatsSummation(BaseVSphereMetricPuller):
    """vCenter Server locking statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.lockstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoLrostatsMaximum(BaseVSphereMetricPuller):
    """vCenter Server LRO statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.lrostats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoLrostatsMinimum(BaseVSphereMetricPuller):
    """vCenter Server LRO statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.lrostats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoLrostatsSummation(BaseVSphereMetricPuller):
    """vCenter Server LRO statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.lrostats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoMiscstatsMaximum(BaseVSphereMetricPuller):
    """Miscellaneous statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.miscstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoMiscstatsMinimum(BaseVSphereMetricPuller):
    """Miscellaneous statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.miscstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoMiscstatsSummation(BaseVSphereMetricPuller):
    """Miscellaneous statistics"""
    metric_group = "host"
    metric_name = "vcDebugInfo.miscstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoMorefregstatsMaximum(BaseVSphereMetricPuller):
    """Managed object reference counts in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.morefregstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoMorefregstatsMinimum(BaseVSphereMetricPuller):
    """Managed object reference counts in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.morefregstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoMorefregstatsSummation(BaseVSphereMetricPuller):
    """Managed object reference counts in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.morefregstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoScoreboardMaximum(BaseVSphereMetricPuller):
    """Object counts in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.scoreboard.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoScoreboardMinimum(BaseVSphereMetricPuller):
    """Object counts in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.scoreboard.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoScoreboardSummation(BaseVSphereMetricPuller):
    """Object counts in vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.scoreboard.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoSessionstatsMaximum(BaseVSphereMetricPuller):
    """The statistics of client sessions connected to vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.sessionstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoSessionstatsMinimum(BaseVSphereMetricPuller):
    """The statistics of client sessions connected to vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.sessionstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoSessionstatsSummation(BaseVSphereMetricPuller):
    """The statistics of client sessions connected to vCenter Server"""
    metric_group = "host"
    metric_name = "vcDebugInfo.sessionstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoSystemstatsMaximum(BaseVSphereMetricPuller):
    """The statistics of vCenter Server as a running system such as thread
    statistics and heap statistics
    """
    metric_group = "host"
    metric_name = "vcDebugInfo.systemstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoSystemstatsMinimum(BaseVSphereMetricPuller):
    """The statistics of vCenter Server as a running system such as thread
    statistics and heap statistics
    """
    metric_group = "host"
    metric_name = "vcDebugInfo.systemstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoSystemstatsSummation(BaseVSphereMetricPuller):
    """The statistics of vCenter Server as a running system such as thread
    statistics and heap statistics
    """
    metric_group = "host"
    metric_name = "vcDebugInfo.systemstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoVcservicestatsMaximum(BaseVSphereMetricPuller):
    """vCenter service statistics such as events, alarms, and tasks"""
    metric_group = "host"
    metric_name = "vcDebugInfo.vcservicestats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoVcservicestatsMinimum(BaseVSphereMetricPuller):
    """vCenter service statistics such as events, alarms, and tasks"""
    metric_group = "host"
    metric_name = "vcDebugInfo.vcservicestats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcDebugInfoVcservicestatsSummation(BaseVSphereMetricPuller):
    """vCenter service statistics such as events, alarms, and tasks"""
    metric_group = "host"
    metric_name = "vcDebugInfo.vcservicestats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesCpuqueuelengthAverage(BaseVSphereMetricPuller):
    """Processor queue length on the system where vCenter Server is running"""
    metric_group = "host"
    metric_name = "vcResources.cpuqueuelength.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesCtxswitchesrateAverage(BaseVSphereMetricPuller):
    """Number of context switches per second on the system where vCenter
    Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.ctxswitchesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesDiskqueuelengthAverage(BaseVSphereMetricPuller):
    """Disk queue length on the system where vCenter Server is running"""
    metric_group = "host"
    metric_name = "vcResources.diskqueuelength.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesDiskreadbytesrateAverage(BaseVSphereMetricPuller):
    """Number of bytes read from the disk per second on the system where
    vCenter Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.diskreadbytesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesDiskreadsrateAverage(BaseVSphereMetricPuller):
    """Number of disk reads per second on the system where vCenter Server is
    running
    """
    metric_group = "host"
    metric_name = "vcResources.diskreadsrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesDiskwritebytesrateAverage(BaseVSphereMetricPuller):
    """Number of bytes written to the disk per second on the system where
    vCenter Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.diskwritebytesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesDiskwritesrateAverage(BaseVSphereMetricPuller):
    """Number of disk writes per second on the system where vCenter Server is
    running
    """
    metric_group = "host"
    metric_name = "vcResources.diskwritesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesNetqueuelengthAverage(BaseVSphereMetricPuller):
    """Network queue length on the system where vCenter Server is running"""
    metric_group = "host"
    metric_name = "vcResources.netqueuelength.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesPacketrateAverage(BaseVSphereMetricPuller):
    """Number of total packets sent and received per second on the system
    where vCenter Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.packetrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesPacketrecvrateAverage(BaseVSphereMetricPuller):
    """Rate of the number of total packets received per second on the system
    where vCenter Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.packetrecvrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesPacketsentrateAverage(BaseVSphereMetricPuller):
    """Number of total packets sent per second on the system where vCenter
    Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.packetsentrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesPagefaultrateAverage(BaseVSphereMetricPuller):
    """Number of page faults per second on the system where vCenter Server is
    running
    """
    metric_group = "host"
    metric_name = "vcResources.pagefaultrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesPhysicalmemusageAverage(BaseVSphereMetricPuller):
    """Physical memory used by vCenter"""
    metric_group = "host"
    metric_name = "vcResources.physicalmemusage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostVcResourcesPoolnonpagedbytesAverage(BaseVSphereMetricPuller):
    """Memory pooled for non-paged bytes on the system where vCenter Server is
    running
    """
    metric_group = "host"
    metric_name = "vcResources.poolnonpagedbytes.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostVcResourcesPoolpagedbytesAverage(BaseVSphereMetricPuller):
    """Memory pooled for paged bytes on the system where vCenter Server is
    running
    """
    metric_group = "host"
    metric_name = "vcResources.poolpagedbytes.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostVcResourcesPriviledgedcpuusageAverage(
        BaseVSphereMetricPuller):
    """CPU used by vCenter Server in privileged mode"""
    metric_group = "host"
    metric_name = "vcResources.priviledgedcpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostVcResourcesProcesscpuusageAverage(BaseVSphereMetricPuller):
    """Total CPU used by vCenter Server"""
    metric_group = "host"
    metric_name = "vcResources.processcpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostVcResourcesProcesshandlesAverage(BaseVSphereMetricPuller):
    """Handles used by vCenter Server"""
    metric_group = "host"
    metric_name = "vcResources.processhandles.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesProcessthreadsAverage(BaseVSphereMetricPuller):
    """Number of threads used by vCenter Server"""
    metric_group = "host"
    metric_name = "vcResources.processthreads.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesSyscallsrateAverage(BaseVSphereMetricPuller):
    """Number of systems calls made per second on the system where vCenter
    Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.syscallsrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesSystemcpuusageAverage(BaseVSphereMetricPuller):
    """Total system CPU used on the system where vCenter Server in running"""
    metric_group = "host"
    metric_name = "vcResources.systemcpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostVcResourcesSystemnetusageAverage(BaseVSphereMetricPuller):
    """Total network bytes received and sent per second on the system where
    vCenter Server is running
    """
    metric_group = "host"
    metric_name = "vcResources.systemnetusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostVcResourcesSystemthreadsAverage(BaseVSphereMetricPuller):
    """Number of threads on the system where vCenter Server is running"""
    metric_group = "host"
    metric_name = "vcResources.systemthreads.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVcResourcesUsercpuusageAverage(BaseVSphereMetricPuller):
    """CPU used by vCenter Server in user mode"""
    metric_group = "host"
    metric_name = "vcResources.usercpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostVcResourcesVirtualmemusageAverage(BaseVSphereMetricPuller):
    """Virtual memory used by vCenter Server"""
    metric_group = "host"
    metric_name = "vcResources.virtualmemusage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereHostVflashModuleNumActiveVMDKsLatest(BaseVSphereMetricPuller):
    """Number of caches controlled by the virtual flash module"""
    metric_group = "host"
    metric_name = "vflashModule.numActiveVMDKs.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskBusResetsSummation(BaseVSphereMetricPuller):
    """Number of resets to a virtual disk"""
    metric_group = "host"
    metric_name = "virtualDisk.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskCommandsAbortedSummation(BaseVSphereMetricPuller):
    """Number of terminations to a virtual disk"""
    metric_group = "host"
    metric_name = "virtualDisk.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskLargeSeeksLatest(BaseVSphereMetricPuller):
    """Number of seeks during the interval that were greater than 8192 LBNs
    apart
    """
    metric_group = "host"
    metric_name = "virtualDisk.largeSeeks.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskMediumSeeksLatest(BaseVSphereMetricPuller):
    """Number of seeks during the interval that were between 64 and 8192 LBNs
    apart
    """
    metric_group = "host"
    metric_name = "virtualDisk.mediumSeeks.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of read commands issued per second to the virtual disk
    during the collection interval
    """
    metric_group = "host"
    metric_name = "virtualDisk.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskNumberWriteAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of write commands issued per second to the virtual disk
    during the collection interval
    """
    metric_group = "host"
    metric_name = "virtualDisk.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data from the virtual disk"""
    metric_group = "host"
    metric_name = "virtualDisk.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostVirtualDiskReadIOSizeLatest(BaseVSphereMetricPuller):
    """Average read request size in bytes"""
    metric_group = "host"
    metric_name = "virtualDisk.readIOSize.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskReadLatencyUSLatest(BaseVSphereMetricPuller):
    """Read latency in microseconds"""
    metric_group = "host"
    metric_name = "virtualDisk.readLatencyUS.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereHostVirtualDiskReadLoadMetricLatest(BaseVSphereMetricPuller):
    """Storage DRS virtual disk metric for the read workload model"""
    metric_group = "host"
    metric_name = "virtualDisk.readLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskReadOIOLatest(BaseVSphereMetricPuller):
    """Average number of outstanding read requests to the virtual disk during
    the collection interval
    """
    metric_group = "host"
    metric_name = "virtualDisk.readOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskSmallSeeksLatest(BaseVSphereMetricPuller):
    """Number of seeks during the interval that were less than 64 LBNs apart"""
    metric_group = "host"
    metric_name = "virtualDisk.smallSeeks.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskThroughputContAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "host"
    metric_name = "virtualDisk.throughput.cont.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVirtualDiskThroughputUsageAverage(BaseVSphereMetricPuller):
    """Virtual disk I/O rate"""
    metric_group = "host"
    metric_name = "virtualDisk.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostVirtualDiskTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read from the virtual disk takes"""
    metric_group = "host"
    metric_name = "virtualDisk.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVirtualDiskTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write to the virtual disk takes"""
    metric_group = "host"
    metric_name = "virtualDisk.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVirtualDiskVFlashCacheIopsLatest(BaseVSphereMetricPuller):
    """The average virtual Flash Read Cache I/Os per second value for the
    virtual disk
    """
    metric_group = "host"
    metric_name = "virtualDisk.vFlashCacheIops.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskVFlashCacheLatencyLatest(BaseVSphereMetricPuller):
    """The average virtual Flash Read Cache latency value for the virtual
    disk
    """
    metric_group = "host"
    metric_name = "virtualDisk.vFlashCacheLatency.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereHostVirtualDiskVFlashCacheThroughputLatest(
        BaseVSphereMetricPuller):
    """The average virtual Flash Read Cache throughput value for the virtual
    disk
    """
    metric_group = "host"
    metric_name = "virtualDisk.vFlashCacheThroughput.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data to the virtual disk"""
    metric_group = "host"
    metric_name = "virtualDisk.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostVirtualDiskWriteIOSizeLatest(BaseVSphereMetricPuller):
    """Average write request size in bytes"""
    metric_group = "host"
    metric_name = "virtualDisk.writeIOSize.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskWriteLatencyUSLatest(BaseVSphereMetricPuller):
    """Write latency in microseconds"""
    metric_group = "host"
    metric_name = "virtualDisk.writeLatencyUS.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereHostVirtualDiskWriteLoadMetricLatest(BaseVSphereMetricPuller):
    """Storage DRS virtual disk metric for the write workload model"""
    metric_group = "host"
    metric_name = "virtualDisk.writeLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVirtualDiskWriteOIOLatest(BaseVSphereMetricPuller):
    """Average number of outstanding write requests to the virtual disk during
    the collection interval
    """
    metric_group = "host"
    metric_name = "virtualDisk.writeOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumChangeDSLatest(BaseVSphereMetricPuller):
    """Number of datastore change operations for powered-off and suspended
    virtual machines
    """
    metric_group = "host"
    metric_name = "vmop.numChangeDS.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumChangeHostLatest(BaseVSphereMetricPuller):
    """Number of host change operations for powered-off and suspended VMs"""
    metric_group = "host"
    metric_name = "vmop.numChangeHost.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumChangeHostDSLatest(BaseVSphereMetricPuller):
    """Number of host and datastore change operations for powered-off and
    suspended virtual machines
    """
    metric_group = "host"
    metric_name = "vmop.numChangeHostDS.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumCloneLatest(BaseVSphereMetricPuller):
    """Number of virtual machine clone operations"""
    metric_group = "host"
    metric_name = "vmop.numClone.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumCreateLatest(BaseVSphereMetricPuller):
    """Number of virtual machine create operations"""
    metric_group = "host"
    metric_name = "vmop.numCreate.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumDeployLatest(BaseVSphereMetricPuller):
    """Number of virtual machine template deploy operations"""
    metric_group = "host"
    metric_name = "vmop.numDeploy.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumDestroyLatest(BaseVSphereMetricPuller):
    """Number of virtual machine delete operations"""
    metric_group = "host"
    metric_name = "vmop.numDestroy.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumPoweroffLatest(BaseVSphereMetricPuller):
    """Number of virtual machine power off operations"""
    metric_group = "host"
    metric_name = "vmop.numPoweroff.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumPoweronLatest(BaseVSphereMetricPuller):
    """Number of virtual machine power on operations"""
    metric_group = "host"
    metric_name = "vmop.numPoweron.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumRebootGuestLatest(BaseVSphereMetricPuller):
    """Number of virtual machine guest reboot operations"""
    metric_group = "host"
    metric_name = "vmop.numRebootGuest.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumReconfigureLatest(BaseVSphereMetricPuller):
    """Number of virtual machine reconfigure operations"""
    metric_group = "host"
    metric_name = "vmop.numReconfigure.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumRegisterLatest(BaseVSphereMetricPuller):
    """Number of virtual machine register operations"""
    metric_group = "host"
    metric_name = "vmop.numRegister.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumResetLatest(BaseVSphereMetricPuller):
    """Number of virtual machine reset operations"""
    metric_group = "host"
    metric_name = "vmop.numReset.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumSVMotionLatest(BaseVSphereMetricPuller):
    """Number of migrations with Storage vMotion (datastore change operations
    for powered-on VMs)
    """
    metric_group = "host"
    metric_name = "vmop.numSVMotion.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumShutdownGuestLatest(BaseVSphereMetricPuller):
    """Number of virtual machine guest shutdown operations"""
    metric_group = "host"
    metric_name = "vmop.numShutdownGuest.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumStandbyGuestLatest(BaseVSphereMetricPuller):
    """Number of virtual machine standby guest operations"""
    metric_group = "host"
    metric_name = "vmop.numStandbyGuest.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumSuspendLatest(BaseVSphereMetricPuller):
    """Number of virtual machine suspend operations"""
    metric_group = "host"
    metric_name = "vmop.numSuspend.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumUnregisterLatest(BaseVSphereMetricPuller):
    """Number of virtual machine unregister operations"""
    metric_group = "host"
    metric_name = "vmop.numUnregister.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumVMotionLatest(BaseVSphereMetricPuller):
    """Number of migrations with vMotion (host change operations for
    powered-on VMs)
    """
    metric_group = "host"
    metric_name = "vmop.numVMotion.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVmopNumXVMotionLatest(BaseVSphereMetricPuller):
    """Number of host and datastore change operations for powered-on and
    suspended virtual machines
    """
    metric_group = "host"
    metric_name = "vmop.numXVMotion.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjReadAvgLatencyAverage(BaseVSphereMetricPuller):
    """Average read latency in ms"""
    metric_group = "host"
    metric_name = "vsanDomObj.readAvgLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVsanDomObjReadCacheHitRateLatest(BaseVSphereMetricPuller):
    """Cache hit rate percentage"""
    metric_group = "host"
    metric_name = "vsanDomObj.readCacheHitRate.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereHostVsanDomObjReadCongestionAverage(BaseVSphereMetricPuller):
    """Read congestion"""
    metric_group = "host"
    metric_name = "vsanDomObj.readCongestion.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjReadIopsAverage(BaseVSphereMetricPuller):
    """Read IOPS"""
    metric_group = "host"
    metric_name = "vsanDomObj.readIops.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjReadMaxLatencyLatest(BaseVSphereMetricPuller):
    """Max read latency in ms"""
    metric_group = "host"
    metric_name = "vsanDomObj.readMaxLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVsanDomObjReadThroughputAverage(BaseVSphereMetricPuller):
    """Read throughput in kBps"""
    metric_group = "host"
    metric_name = "vsanDomObj.readThroughput.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostVsanDomObjRecoveryWriteAvgLatencyAverage(
        BaseVSphereMetricPuller):
    """Average recovery write latency in ms"""
    metric_group = "host"
    metric_name = "vsanDomObj.recoveryWriteAvgLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVsanDomObjRecoveryWriteCongestionAverage(
        BaseVSphereMetricPuller):
    """Recovery write congestion"""
    metric_group = "host"
    metric_name = "vsanDomObj.recoveryWriteCongestion.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjRecoveryWriteIopsAverage(BaseVSphereMetricPuller):
    """Recovery write IOPS"""
    metric_group = "host"
    metric_name = "vsanDomObj.recoveryWriteIops.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjRecoveryWriteMaxLatencyLatest(
        BaseVSphereMetricPuller):
    """Max recovery write latency in ms"""
    metric_group = "host"
    metric_name = "vsanDomObj.recoveryWriteMaxLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVsanDomObjRecoveryWriteThroughputAverage(
        BaseVSphereMetricPuller):
    """Recovery write through-put in kBps"""
    metric_group = "host"
    metric_name = "vsanDomObj.recoveryWriteThroughput.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereHostVsanDomObjWriteAvgLatencyAverage(BaseVSphereMetricPuller):
    """Average write latency in ms"""
    metric_group = "host"
    metric_name = "vsanDomObj.writeAvgLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVsanDomObjWriteCongestionAverage(BaseVSphereMetricPuller):
    """Write congestion"""
    metric_group = "host"
    metric_name = "vsanDomObj.writeCongestion.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjWriteIopsAverage(BaseVSphereMetricPuller):
    """Write IOPS"""
    metric_group = "host"
    metric_name = "vsanDomObj.writeIops.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereHostVsanDomObjWriteMaxLatencyLatest(BaseVSphereMetricPuller):
    """Max write latency in ms"""
    metric_group = "host"
    metric_name = "vsanDomObj.writeMaxLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereHostVsanDomObjWriteThroughputAverage(BaseVSphereMetricPuller):
    """Write throughput in kBps"""
    metric_group = "host"
    metric_name = "vsanDomObj.writeThroughput.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10
