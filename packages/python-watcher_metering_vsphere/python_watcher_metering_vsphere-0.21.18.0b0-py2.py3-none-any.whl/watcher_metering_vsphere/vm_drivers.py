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


class VSphereVmClusterServicesCpufairnessLatest(BaseVSphereMetricPuller):
    """Fairness of distributed CPU resource allocation"""
    metric_group = "vm"
    metric_name = "clusterServices.cpufairness.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmClusterServicesEffectivecpuAverage(BaseVSphereMetricPuller):
    """Total available CPU resources of all hosts within a cluster"""
    metric_group = "vm"
    metric_name = "clusterServices.effectivecpu.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmClusterServicesEffectivememAverage(BaseVSphereMetricPuller):
    """Total amount of machine memory of all hosts in the cluster that is
    available for use for virtual machine memory and overhead memory
    """
    metric_group = "vm"
    metric_name = "clusterServices.effectivemem.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmClusterServicesFailoverLatest(BaseVSphereMetricPuller):
    """vSphere HA number of failures that can be tolerated"""
    metric_group = "vm"
    metric_name = "clusterServices.failover.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmClusterServicesMemfairnessLatest(BaseVSphereMetricPuller):
    """Aggregate available memory resources of all the hosts within a
    cluster
    """
    metric_group = "vm"
    metric_name = "clusterServices.memfairness.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmCpuCapacityContentionAverage(BaseVSphereMetricPuller):
    """Percent of time the VM is unable to run because it is contending for
    access to the physical CPU(s)
    """
    metric_group = "vm"
    metric_name = "cpu.capacity.contention.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuCapacityDemandAverage(BaseVSphereMetricPuller):
    """The amount of CPU resources a VM would use if there were no CPU
    contention or CPU limit
    """
    metric_group = "vm"
    metric_name = "cpu.capacity.demand.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuCapacityEntitlementAverage(BaseVSphereMetricPuller):
    """CPU resources devoted by the ESXi scheduler to the virtual machines and
    resource pools
    """
    metric_group = "vm"
    metric_name = "cpu.capacity.entitlement.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuCapacityProvisionedAverage(BaseVSphereMetricPuller):
    """Capacity in MHz of the physical CPU cores"""
    metric_group = "vm"
    metric_name = "cpu.capacity.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuCapacityUsageAverage(BaseVSphereMetricPuller):
    """CPU usage as a percent during the interval."""
    metric_group = "vm"
    metric_name = "cpu.capacity.usage.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuCoreUtilization(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "vm"
    metric_name = "cpu.coreUtilization"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuCoreUtilizationAverage(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "vm"
    metric_name = "cpu.coreUtilization.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuCoreUtilizationMaximum(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "vm"
    metric_name = "cpu.coreUtilization.maximum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuCoreUtilizationMinimum(BaseVSphereMetricPuller):
    """CPU utilization of the corresponding core (if hyper-threading is
    enabled) as a percentage during the interval (A core is utilized if either
    or both of its logical CPUs are utilized)
    """
    metric_group = "vm"
    metric_name = "cpu.coreUtilization.minimum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuCorecountContentionAverage(BaseVSphereMetricPuller):
    """Time the VM vCPU is ready to run, but is unable to run due to
    co-scheduling constraints
    """
    metric_group = "vm"
    metric_name = "cpu.corecount.contention.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuCorecountProvisionedAverage(BaseVSphereMetricPuller):
    """The number of virtual processors provisioned to the entity."""
    metric_group = "vm"
    metric_name = "cpu.corecount.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmCpuCorecountUsageAverage(BaseVSphereMetricPuller):
    """The number of virtual processors running on the host."""
    metric_group = "vm"
    metric_name = "cpu.corecount.usage.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmCpuCostopSummation(BaseVSphereMetricPuller):
    """Time the virtual machine is ready to run, but is unable to run due to
    co-scheduling constraints
    """
    metric_group = "vm"
    metric_name = "cpu.costop.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuCpuentitlementLatest(BaseVSphereMetricPuller):
    """Amount of CPU resources allocated to the virtual machine or resource
    pool, based on the total cluster capacity and the resource configuration
    of the resource hierarchy
    """
    metric_group = "vm"
    metric_name = "cpu.cpuentitlement.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuDemandAverage(BaseVSphereMetricPuller):
    """The amount of CPU resources a virtual machine would use if there were
    no CPU contention or CPU limit
    """
    metric_group = "vm"
    metric_name = "cpu.demand.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuDemandEntitlementRatioLatest(BaseVSphereMetricPuller):
    """CPU resource entitlement to CPU demand ratio (in percents)"""
    metric_group = "vm"
    metric_name = "cpu.demandEntitlementRatio.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuEntitlementLatest(BaseVSphereMetricPuller):
    """CPU resources devoted by the ESX scheduler"""
    metric_group = "vm"
    metric_name = "cpu.entitlement.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuIdleSummation(BaseVSphereMetricPuller):
    """Total time that the CPU spent in an idle state"""
    metric_group = "vm"
    metric_name = "cpu.idle.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuLatencyAverage(BaseVSphereMetricPuller):
    """Percent of time the virtual machine is unable to run because it is
    contending for access to the physical CPU(s)
    """
    metric_group = "vm"
    metric_name = "cpu.latency.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuMaxlimitedSummation(BaseVSphereMetricPuller):
    """Time the virtual machine is ready to run, but is not run due to maxing
    out its CPU limit setting
    """
    metric_group = "vm"
    metric_name = "cpu.maxlimited.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuOverlapSummation(BaseVSphereMetricPuller):
    """Time the virtual machine was interrupted to perform system services on
    behalf of itself or other virtual machines
    """
    metric_group = "vm"
    metric_name = "cpu.overlap.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuReadinessAverage(BaseVSphereMetricPuller):
    """Percentage of time that the virtual machine was ready, but could not
    get scheduled to run on the physical CPU
    """
    metric_group = "vm"
    metric_name = "cpu.readiness.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuReadySummation(BaseVSphereMetricPuller):
    """Time that the virtual machine was ready, but could not get scheduled to
    run on the physical CPU during last measurement interval
    """
    metric_group = "vm"
    metric_name = "cpu.ready.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuReservedCapacityAverage(BaseVSphereMetricPuller):
    """Total CPU capacity reserved by virtual machines"""
    metric_group = "vm"
    metric_name = "cpu.reservedCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuRunSummation(BaseVSphereMetricPuller):
    """Time the virtual machine is scheduled to run"""
    metric_group = "vm"
    metric_name = "cpu.run.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuSwapwaitSummation(BaseVSphereMetricPuller):
    """CPU time spent waiting for swap-in"""
    metric_group = "vm"
    metric_name = "cpu.swapwait.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuSystemSummation(BaseVSphereMetricPuller):
    """Amount of time spent on system processes on each virtual CPU in the
    virtual machine
    """
    metric_group = "vm"
    metric_name = "cpu.system.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuTotalCapacityAverage(BaseVSphereMetricPuller):
    """Total CPU capacity reserved by and available for virtual machines"""
    metric_group = "vm"
    metric_name = "cpu.totalCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuTotalmhzAverage(BaseVSphereMetricPuller):
    """Total amount of CPU resources of all hosts in the cluster"""
    metric_group = "vm"
    metric_name = "cpu.totalmhz.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuUsage(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usage"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUsageAverage(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUsageMaximum(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usage.maximum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUsageMinimum(BaseVSphereMetricPuller):
    """CPU usage as a percentage during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usage.minimum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUsagemhz(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usagemhz"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuUsagemhzAverage(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usagemhz.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuUsagemhzMaximum(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usagemhz.maximum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuUsagemhzMinimum(BaseVSphereMetricPuller):
    """CPU usage in megahertz during the interval"""
    metric_group = "vm"
    metric_name = "cpu.usagemhz.minimum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmCpuUsedSummation(BaseVSphereMetricPuller):
    """Total CPU usage"""
    metric_group = "vm"
    metric_name = "cpu.used.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmCpuUtilization(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "vm"
    metric_name = "cpu.utilization"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUtilizationAverage(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "vm"
    metric_name = "cpu.utilization.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUtilizationMaximum(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "vm"
    metric_name = "cpu.utilization.maximum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuUtilizationMinimum(BaseVSphereMetricPuller):
    """CPU utilization as a percentage during the interval (CPU usage and CPU
    utilization might be different due to power management technologies or
    hyper-threading)
    """
    metric_group = "vm"
    metric_name = "cpu.utilization.minimum"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmCpuWaitSummation(BaseVSphereMetricPuller):
    """Total CPU time spent in wait state"""
    metric_group = "vm"
    metric_name = "cpu.wait.summation"
    metric_type = "delta"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDatastoreBusResetsSummation(BaseVSphereMetricPuller):
    """busResets"""
    metric_group = "vm"
    metric_name = "datastore.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreCommandsAbortedSummation(BaseVSphereMetricPuller):
    """commandsAborted"""
    metric_group = "vm"
    metric_name = "datastore.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreIopsAverage(BaseVSphereMetricPuller):
    """Storage I/O Control aggregated IOPS"""
    metric_group = "vm"
    metric_name = "datastore.datastoreIops.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreMaxQueueDepthLatest(BaseVSphereMetricPuller):
    """Storage I/O Control datastore maximum queue depth"""
    metric_group = "vm"
    metric_name = "datastore.datastoreMaxQueueDepth.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreNormalReadLatencyLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore normalized read latency"""
    metric_group = "vm"
    metric_name = "datastore.datastoreNormalReadLatency.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreNormalWriteLatencyLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore normalized write latency"""
    metric_group = "vm"
    metric_name = "datastore.datastoreNormalWriteLatency.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreReadBytesLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore bytes read"""
    metric_group = "vm"
    metric_name = "datastore.datastoreReadBytes.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreReadIopsLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore read I/O rate"""
    metric_group = "vm"
    metric_name = "datastore.datastoreReadIops.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreReadLoadMetricLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore metric for read workload model"""
    metric_group = "vm"
    metric_name = "datastore.datastoreReadLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreReadOIOLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore outstanding read requests"""
    metric_group = "vm"
    metric_name = "datastore.datastoreReadOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreVMObservedLatencyLatest(
        BaseVSphereMetricPuller):
    """The average datastore latency as seen by virtual machines"""
    metric_group = "vm"
    metric_name = "datastore.datastoreVMObservedLatency.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreWriteBytesLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore bytes written"""
    metric_group = "vm"
    metric_name = "datastore.datastoreWriteBytes.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreWriteIopsLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore write I/O rate"""
    metric_group = "vm"
    metric_name = "datastore.datastoreWriteIops.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreWriteLoadMetricLatest(
        BaseVSphereMetricPuller):
    """Storage DRS datastore metric for write workload model"""
    metric_group = "vm"
    metric_name = "datastore.datastoreWriteLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreDatastoreWriteOIOLatest(BaseVSphereMetricPuller):
    """Storage DRS datastore outstanding write requests"""
    metric_group = "vm"
    metric_name = "datastore.datastoreWriteOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all datastores used by the host"""
    metric_group = "vm"
    metric_name = "datastore.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDatastoreNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of read commands issued per second to the datastore
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "datastore.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreNumberWriteAveragedAverage(BaseVSphereMetricPuller):
    """Average number of write commands issued per second to the datastore
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "datastore.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDatastoreReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data from the datastore"""
    metric_group = "vm"
    metric_name = "datastore.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDatastoreSiocActiveTimePercentageAverage(
        BaseVSphereMetricPuller):
    """Percentage of time Storage I/O Control actively controlled datastore
    latency
    """
    metric_group = "vm"
    metric_name = "datastore.siocActiveTimePercentage.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmDatastoreSizeNormalizedDatastoreLatencyAverage(
        BaseVSphereMetricPuller):
    """Storage I/O Control size-normalized I/O latency"""
    metric_group = "vm"
    metric_name = "datastore.sizeNormalizedDatastoreLatency.average"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereVmDatastoreThroughputContentionAverage(BaseVSphereMetricPuller):
    """contention"""
    metric_group = "vm"
    metric_name = "datastore.throughput.contention.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDatastoreThroughputUsageAverage(BaseVSphereMetricPuller):
    """usage"""
    metric_group = "vm"
    metric_name = "datastore.throughput.usage.average"
    metric_type = "cumulative"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDatastoreTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read from the datastore takes"""
    metric_group = "vm"
    metric_name = "datastore.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDatastoreTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write to the datastore takes"""
    metric_group = "vm"
    metric_name = "datastore.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDatastoreWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data to the datastore"""
    metric_group = "vm"
    metric_name = "datastore.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskBusResetsSummation(BaseVSphereMetricPuller):
    """Number of SCSI-bus reset commands issued during the collection
    interval
    """
    metric_group = "vm"
    metric_name = "disk.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskCapacityContentionAverage(BaseVSphereMetricPuller):
    """contention"""
    metric_group = "vm"
    metric_name = "disk.capacity.contention.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmDiskCapacityLatest(BaseVSphereMetricPuller):
    """Configured size of the datastore"""
    metric_group = "vm"
    metric_name = "disk.capacity.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskCapacityProvisionedAverage(BaseVSphereMetricPuller):
    """provisioned"""
    metric_group = "vm"
    metric_name = "disk.capacity.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskCapacityUsageAverage(BaseVSphereMetricPuller):
    """usage"""
    metric_group = "vm"
    metric_name = "disk.capacity.usage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskCommandsSummation(BaseVSphereMetricPuller):
    """Number of SCSI commands issued during the collection interval"""
    metric_group = "vm"
    metric_name = "disk.commands.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskCommandsAbortedSummation(BaseVSphereMetricPuller):
    """Number of SCSI commands aborted during the collection interval"""
    metric_group = "vm"
    metric_name = "disk.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskCommandsAveragedAverage(BaseVSphereMetricPuller):
    """Average number of SCSI commands issued per second during the collection
    interval
    """
    metric_group = "vm"
    metric_name = "disk.commandsAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskDeltausedLatest(BaseVSphereMetricPuller):
    """Storage overhead of a virtual machine or a datastore due to delta disk
    backings
    """
    metric_group = "vm"
    metric_name = "disk.deltaused.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskDeviceLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, to complete a SCSI command
    from the physical device
    """
    metric_group = "vm"
    metric_name = "disk.deviceLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskDeviceReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, to read from the physical
    device
    """
    metric_group = "vm"
    metric_name = "disk.deviceReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskDeviceWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, to write to the physical
    device
    """
    metric_group = "vm"
    metric_name = "disk.deviceWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskKernelLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, spent by VMkernel to process
    each SCSI command
    """
    metric_group = "vm"
    metric_name = "disk.kernelLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskKernelReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, spent by VMkernel to process
    each SCSI read command
    """
    metric_group = "vm"
    metric_name = "disk.kernelReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskKernelWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time, in milliseconds, spent by VMkernel to process
    each SCSI write command
    """
    metric_group = "vm"
    metric_name = "disk.kernelWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskMaxQueueDepthAverage(BaseVSphereMetricPuller):
    """Maximum queue depth"""
    metric_group = "vm"
    metric_name = "disk.maxQueueDepth.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all disks used by the host"""
    metric_group = "vm"
    metric_name = "disk.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskNumberReadSummation(BaseVSphereMetricPuller):
    """Number of disk reads during the collection interval"""
    metric_group = "vm"
    metric_name = "disk.numberRead.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of disk reads per second during the collection
    interval
    """
    metric_group = "vm"
    metric_name = "disk.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskNumberWriteSummation(BaseVSphereMetricPuller):
    """Number of disk writes during the collection interval"""
    metric_group = "vm"
    metric_name = "disk.numberWrite.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskNumberWriteAveragedAverage(BaseVSphereMetricPuller):
    """Average number of disk writes per second during the collection
    interval
    """
    metric_group = "vm"
    metric_name = "disk.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskProvisionedLatest(BaseVSphereMetricPuller):
    """Amount of storage set aside for use by a datastore or a virtual
    machine
    """
    metric_group = "vm"
    metric_name = "disk.provisioned.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskQueueLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI command,
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "disk.queueLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskQueueReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI read
    command, during the collection interval
    """
    metric_group = "vm"
    metric_name = "disk.queueReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskQueueWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI write
    command, during the collection interval
    """
    metric_group = "vm"
    metric_name = "disk.queueWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskReadAverage(BaseVSphereMetricPuller):
    """Average number of kilobytes read from the disk each second during the
    collection interval
    """
    metric_group = "vm"
    metric_name = "disk.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskScsiReservationCnflctsPctAverage(BaseVSphereMetricPuller):
    """Number of SCSI reservation conflicts for the LUN as a percent of total
    commands during the collection interval
    """
    metric_group = "vm"
    metric_name = "disk.scsiReservationCnflctsPct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmDiskScsiReservationConflictsSummation(BaseVSphereMetricPuller):
    """Number of SCSI reservation conflicts for the LUN during the collection
    interval
    """
    metric_group = "vm"
    metric_name = "disk.scsiReservationConflicts.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmDiskThroughputContentionAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "vm"
    metric_name = "disk.throughput.contention.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskThroughputUsageAverage(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate, including the rates for all virtual machines
    running on the host during the collection interval
    """
    metric_group = "vm"
    metric_name = "disk.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskTotalLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time taken during the collection interval to process
    a SCSI command issued by the guest OS to the virtual machine
    """
    metric_group = "vm"
    metric_name = "disk.totalLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time taken during the collection interval to process
    a SCSI read command issued from the guest OS to the virtual machine
    """
    metric_group = "vm"
    metric_name = "disk.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time taken during the collection interval to process
    a SCSI write command issued by the guest OS to the virtual machine
    """
    metric_group = "vm"
    metric_name = "disk.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmDiskUnsharedLatest(BaseVSphereMetricPuller):
    """Amount of space associated exclusively with a virtual machine"""
    metric_group = "vm"
    metric_name = "disk.unshared.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskUsage(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "vm"
    metric_name = "disk.usage"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskUsageAverage(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "vm"
    metric_name = "disk.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskUsageMaximum(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "vm"
    metric_name = "disk.usage.maximum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskUsageMinimum(BaseVSphereMetricPuller):
    """Aggregated disk I/O rate. For hosts, this metric includes the rates for
    all virtual machines running on the host during the collection
    interval.
    """
    metric_group = "vm"
    metric_name = "disk.usage.minimum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmDiskUsedLatest(BaseVSphereMetricPuller):
    """Amount of space actually used by the virtual machine or the datastore"""
    metric_group = "vm"
    metric_name = "disk.used.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmDiskWriteAverage(BaseVSphereMetricPuller):
    """Average number of kilobytes written to disk each second during the
    collection interval
    """
    metric_group = "vm"
    metric_name = "disk.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmHbrHbrNetRxAverage(BaseVSphereMetricPuller):
    """Average amount of data received per second"""
    metric_group = "vm"
    metric_name = "hbr.hbrNetRx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmHbrHbrNetTxAverage(BaseVSphereMetricPuller):
    """Average amount of data transmitted per second"""
    metric_group = "vm"
    metric_name = "hbr.hbrNetTx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmHbrHbrNumVmsAverage(BaseVSphereMetricPuller):
    """Current number of replicated virtual machines"""
    metric_group = "vm"
    metric_name = "hbr.hbrNumVms.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmManagementAgentCpuUsageAverage(BaseVSphereMetricPuller):
    """Amount of Service Console CPU usage"""
    metric_group = "vm"
    metric_name = "managementAgent.cpuUsage.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmManagementAgentMemUsedAverage(BaseVSphereMetricPuller):
    """Amount of total configured memory that is available for use"""
    metric_group = "vm"
    metric_name = "managementAgent.memUsed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmManagementAgentSwapInAverage(BaseVSphereMetricPuller):
    """Amount of memory that is swapped in for the Service Console"""
    metric_group = "vm"
    metric_name = "managementAgent.swapIn.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmManagementAgentSwapOutAverage(BaseVSphereMetricPuller):
    """Amount of memory that is swapped out for the Service Console"""
    metric_group = "vm"
    metric_name = "managementAgent.swapOut.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmManagementAgentSwapUsedAverage(BaseVSphereMetricPuller):
    """Sum of the memory swapped by all powered-on virtual machines on the
    host
    """
    metric_group = "vm"
    metric_name = "managementAgent.swapUsed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemActive(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "vm"
    metric_name = "mem.active"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemActiveAverage(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "vm"
    metric_name = "mem.active.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemActiveMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "vm"
    metric_name = "mem.active.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemActiveMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is actively used, as estimated by VMkernel based
    on recently touched memory pages
    """
    metric_group = "vm"
    metric_name = "mem.active.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemActivewriteAverage(BaseVSphereMetricPuller):
    """Estimate for the amount of memory actively being written to by the
    virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.activewrite.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityContentionAverage(BaseVSphereMetricPuller):
    """Percentage of time VMs are waiting to access swapped, compressed or
    ballooned memory
    """
    metric_group = "vm"
    metric_name = "mem.capacity.contention.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemCapacityEntitlementAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory the VM is entitled to, as determined by
    the ESXi scheduler
    """
    metric_group = "vm"
    metric_name = "mem.capacity.entitlement.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityProvisionedAverage(BaseVSphereMetricPuller):
    """Total amount of memory available to the host"""
    metric_group = "vm"
    metric_name = "mem.capacity.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityUsableAverage(BaseVSphereMetricPuller):
    """Amount of physical memory available for use by virtual machines on this
    host
    """
    metric_group = "vm"
    metric_name = "mem.capacity.usable.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityUsageAverage(BaseVSphereMetricPuller):
    """Amount of physical memory actively used"""
    metric_group = "vm"
    metric_name = "mem.capacity.usage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityUsageUserworldAverage(BaseVSphereMetricPuller):
    """userworld"""
    metric_group = "vm"
    metric_name = "mem.capacity.usage.userworld.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityUsageVmAverage(BaseVSphereMetricPuller):
    """vm"""
    metric_group = "vm"
    metric_name = "mem.capacity.usage.vm.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityUsageVmOvrhdAverage(BaseVSphereMetricPuller):
    """vmOvrhd"""
    metric_group = "vm"
    metric_name = "mem.capacity.usage.vmOvrhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCapacityUsageVmkOvrhdAverage(BaseVSphereMetricPuller):
    """vmkOvrhd"""
    metric_group = "vm"
    metric_name = "mem.capacity.usage.vmkOvrhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCompressedAverage(BaseVSphereMetricPuller):
    """Amount of guest physical memory compressed by ESX/ESXi"""
    metric_group = "vm"
    metric_name = "mem.compressed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemCompressionRateAverage(BaseVSphereMetricPuller):
    """Rate of memory compression for the virtual machine"""
    metric_group = "vm"
    metric_name = "mem.compressionRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmMemConsumed(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "vm"
    metric_name = "mem.consumed"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemConsumedAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "vm"
    metric_name = "mem.consumed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemConsumedMaximum(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "vm"
    metric_name = "mem.consumed.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemConsumedMinimum(BaseVSphereMetricPuller):
    """Amount of host physical memory consumed by a virtual machine, host, or
    cluster
    """
    metric_group = "vm"
    metric_name = "mem.consumed.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemConsumedUserworldsAverage(BaseVSphereMetricPuller):
    """Amount of physical memory consumed by userworlds on this host"""
    metric_group = "vm"
    metric_name = "mem.consumed.userworlds.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemConsumedVmsAverage(BaseVSphereMetricPuller):
    """Amount of physical memory consumed by VMs on this host"""
    metric_group = "vm"
    metric_name = "mem.consumed.vms.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemDecompressionRateAverage(BaseVSphereMetricPuller):
    """Rate of memory decompression for the virtual machine"""
    metric_group = "vm"
    metric_name = "mem.decompressionRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmMemEntitlementAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory the virtual machine is entitled to, as
    determined by the ESX scheduler
    """
    metric_group = "vm"
    metric_name = "mem.entitlement.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemGranted(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "vm"
    metric_name = "mem.granted"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemGrantedAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "vm"
    metric_name = "mem.granted.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemGrantedMaximum(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "vm"
    metric_name = "mem.granted.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemGrantedMinimum(BaseVSphereMetricPuller):
    """Amount of host physical memory or physical memory that is mapped for a
    virtual machine or a host
    """
    metric_group = "vm"
    metric_name = "mem.granted.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeap(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "vm"
    metric_name = "mem.heap"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapAverage(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "vm"
    metric_name = "mem.heap.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapMaximum(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "vm"
    metric_name = "mem.heap.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapMinimum(BaseVSphereMetricPuller):
    """VMkernel virtual address space dedicated to VMkernel main heap and
    related data
    """
    metric_group = "vm"
    metric_name = "mem.heap.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapfree(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "vm"
    metric_name = "mem.heapfree"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapfreeAverage(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "vm"
    metric_name = "mem.heapfree.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapfreeMaximum(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "vm"
    metric_name = "mem.heapfree.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemHeapfreeMinimum(BaseVSphereMetricPuller):
    """Free address space in the VMkernel main heap"""
    metric_group = "vm"
    metric_name = "mem.heapfree.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLatencyAverage(BaseVSphereMetricPuller):
    """Percentage of time the virtual machine is waiting to access swapped or
    compressed memory
    """
    metric_group = "vm"
    metric_name = "mem.latency.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemLlSwapIn(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapIn"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapInAverage(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapIn.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapInMaximum(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapIn.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapInMinimum(BaseVSphereMetricPuller):
    """Amount of memory swapped-in from host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapIn.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapInRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is being swapped from host cache into active
    memory
    """
    metric_group = "vm"
    metric_name = "mem.llSwapInRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmMemLlSwapOut(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapOut"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapOutAverage(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapOut.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapOutMaximum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapOut.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapOutMinimum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapOut.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapOutRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is being swapped from active memory to host
    cache
    """
    metric_group = "vm"
    metric_name = "mem.llSwapOutRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmMemLlSwapUsed(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapUsed"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapUsedAverage(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapUsed.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapUsedMaximum(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapUsed.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLlSwapUsedMinimum(BaseVSphereMetricPuller):
    """Space used for caching swapped pages in the host cache"""
    metric_group = "vm"
    metric_name = "mem.llSwapUsed.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemLowfreethresholdAverage(BaseVSphereMetricPuller):
    """Threshold of free host physical memory below which ESX/ESXi will begin
    reclaiming memory from virtual machines through ballooning and swapping
    """
    metric_group = "vm"
    metric_name = "mem.lowfreethreshold.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemMementitlementLatest(BaseVSphereMetricPuller):
    """Memory allocation as calculated by the VMkernel scheduler based on
    current estimated demand and reservation, limit, and shares policies set
    for all virtual machines and resource pools in the host or cluster
    """
    metric_group = "vm"
    metric_name = "mem.mementitlement.latest"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmMemOverhead(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.overhead"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemOverheadAverage(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.overhead.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemOverheadMaximum(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.overhead.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemOverheadMinimum(BaseVSphereMetricPuller):
    """Host physical memory (KB) consumed by the virtualization infrastructure
    for running the virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.overhead.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemOverheadMaxAverage(BaseVSphereMetricPuller):
    """Host physical memory (KB) reserved for use as the virtualization
    overhead for the virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.overheadMax.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemOverheadTouchedAverage(BaseVSphereMetricPuller):
    """Actively touched overhead host physical memory (KB) reserved for use as
    the virtualization overhead for the virtual machine
    """
    metric_group = "vm"
    metric_name = "mem.overheadTouched.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemReservedCapacityAverage(BaseVSphereMetricPuller):
    """Total amount of memory reservation used by powered-on virtual machines
    and vSphere services on the host
    """
    metric_group = "vm"
    metric_name = "mem.reservedCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmMemReservedCapacityUserworldAverage(BaseVSphereMetricPuller):
    """userworld"""
    metric_group = "vm"
    metric_name = "mem.reservedCapacity.userworld.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemReservedCapacityVmAverage(BaseVSphereMetricPuller):
    """vm"""
    metric_group = "vm"
    metric_name = "mem.reservedCapacity.vm.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemReservedCapacityVmOvhdAverage(BaseVSphereMetricPuller):
    """vmOvhd"""
    metric_group = "vm"
    metric_name = "mem.reservedCapacity.vmOvhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemReservedCapacityVmkOvrhdAverage(BaseVSphereMetricPuller):
    """vmkOvrhd"""
    metric_group = "vm"
    metric_name = "mem.reservedCapacity.vmkOvrhd.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemReservedCapacityPctAverage(BaseVSphereMetricPuller):
    """Percent of memory that has been reserved either through VMkernel use,
    by userworlds or due to VM memory reservations
    """
    metric_group = "vm"
    metric_name = "mem.reservedCapacityPct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemShared(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "vm"
    metric_name = "mem.shared"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedAverage(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "vm"
    metric_name = "mem.shared.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedMaximum(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "vm"
    metric_name = "mem.shared.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedMinimum(BaseVSphereMetricPuller):
    """Amount of guest physical memory that is shared with other virtual
    machines, relative to a single virtual machine or to all powered-on
    virtual machines on a host
    """
    metric_group = "vm"
    metric_name = "mem.shared.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedcommon(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "vm"
    metric_name = "mem.sharedcommon"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedcommonAverage(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "vm"
    metric_name = "mem.sharedcommon.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedcommonMaximum(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "vm"
    metric_name = "mem.sharedcommon.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSharedcommonMinimum(BaseVSphereMetricPuller):
    """Amount of machine memory that is shared by all powered-on virtual
    machines and vSphere services on the host
    """
    metric_group = "vm"
    metric_name = "mem.sharedcommon.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemStateLatest(BaseVSphereMetricPuller):
    """One of four threshold levels representing the percentage of free memory
    on the host. The counter value determines swapping and ballooning behavior
    for memory reclamation.
    """
    metric_group = "vm"
    metric_name = "mem.state.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmMemSwapIn(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "vm"
    metric_name = "mem.swapIn"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapInAverage(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "vm"
    metric_name = "mem.swapIn.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapInMaximum(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "vm"
    metric_name = "mem.swapIn.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapInMinimum(BaseVSphereMetricPuller):
    """swapIn"""
    metric_group = "vm"
    metric_name = "mem.swapIn.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapOut(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "vm"
    metric_name = "mem.swapOut"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapOutAverage(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "vm"
    metric_name = "mem.swapOut.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapOutMaximum(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "vm"
    metric_name = "mem.swapOut.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapOutMinimum(BaseVSphereMetricPuller):
    """swapOut"""
    metric_group = "vm"
    metric_name = "mem.swapOut.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapin(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "vm"
    metric_name = "mem.swapin"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapinAverage(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "vm"
    metric_name = "mem.swapin.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapinMaximum(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "vm"
    metric_name = "mem.swapin.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapinMinimum(BaseVSphereMetricPuller):
    """Amount swapped-in to memory from disk"""
    metric_group = "vm"
    metric_name = "mem.swapin.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapinRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is swapped from disk into active memory during the
    interval
    """
    metric_group = "vm"
    metric_name = "mem.swapinRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmMemSwapout(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "vm"
    metric_name = "mem.swapout"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapoutAverage(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "vm"
    metric_name = "mem.swapout.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapoutMaximum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "vm"
    metric_name = "mem.swapout.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapoutMinimum(BaseVSphereMetricPuller):
    """Amount of memory swapped-out to disk"""
    metric_group = "vm"
    metric_name = "mem.swapout.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapoutRateAverage(BaseVSphereMetricPuller):
    """Rate at which memory is being swapped from active memory to disk during
    the current interval
    """
    metric_group = "vm"
    metric_name = "mem.swapoutRate.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmMemSwapped(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "vm"
    metric_name = "mem.swapped"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwappedAverage(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "vm"
    metric_name = "mem.swapped.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwappedMaximum(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "vm"
    metric_name = "mem.swapped.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwappedMinimum(BaseVSphereMetricPuller):
    """Current amount of guest physical memory swapped out to the virtual
    machine swap file by the VMkernel
    """
    metric_group = "vm"
    metric_name = "mem.swapped.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwaptarget(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "vm"
    metric_name = "mem.swaptarget"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwaptargetAverage(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "vm"
    metric_name = "mem.swaptarget.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwaptargetMaximum(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "vm"
    metric_name = "mem.swaptarget.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwaptargetMinimum(BaseVSphereMetricPuller):
    """Target size for the virtual machine swap file"""
    metric_group = "vm"
    metric_name = "mem.swaptarget.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapunreserved(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "vm"
    metric_name = "mem.swapunreserved"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapunreservedAverage(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "vm"
    metric_name = "mem.swapunreserved.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapunreservedMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "vm"
    metric_name = "mem.swapunreserved.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapunreservedMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved by swap"""
    metric_group = "vm"
    metric_name = "mem.swapunreserved.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapused(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "vm"
    metric_name = "mem.swapused"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapusedAverage(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "vm"
    metric_name = "mem.swapused.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapusedMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "vm"
    metric_name = "mem.swapused.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSwapusedMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is used by swap"""
    metric_group = "vm"
    metric_name = "mem.swapused.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSysUsage(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "vm"
    metric_name = "mem.sysUsage"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSysUsageAverage(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "vm"
    metric_name = "mem.sysUsage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSysUsageMaximum(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "vm"
    metric_name = "mem.sysUsage.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemSysUsageMinimum(BaseVSphereMetricPuller):
    """Amount of host physical memory used by VMkernel for core functionality,
    such as device drivers and other internal uses
    """
    metric_group = "vm"
    metric_name = "mem.sysUsage.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemTotalCapacityAverage(BaseVSphereMetricPuller):
    """Total amount of memory reservation used by and available for powered-on
    virtual machines and vSphere services on the host
    """
    metric_group = "vm"
    metric_name = "mem.totalCapacity.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmMemTotalmbAverage(BaseVSphereMetricPuller):
    """Total amount of host physical memory of all hosts in the cluster that
    is available for virtual machine memory (physical memory for use by the
    guest OS) and virtual machine overhead memory
    """
    metric_group = "vm"
    metric_name = "mem.totalmb.average"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmMemUnreserved(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "vm"
    metric_name = "mem.unreserved"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemUnreservedAverage(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "vm"
    metric_name = "mem.unreserved.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemUnreservedMaximum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "vm"
    metric_name = "mem.unreserved.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemUnreservedMinimum(BaseVSphereMetricPuller):
    """Amount of memory that is unreserved"""
    metric_group = "vm"
    metric_name = "mem.unreserved.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemUsage(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "vm"
    metric_name = "mem.usage"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemUsageAverage(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "vm"
    metric_name = "mem.usage.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemUsageMaximum(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "vm"
    metric_name = "mem.usage.maximum"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemUsageMinimum(BaseVSphereMetricPuller):
    """Memory usage as percentage of total configured or available memory"""
    metric_group = "vm"
    metric_name = "mem.usage.minimum"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemVmfsPbcCapMissRatioLatest(BaseVSphereMetricPuller):
    """Trailing average of the ratio of capacity misses to compulsory misses
    for the VMFS PB Cache
    """
    metric_group = "vm"
    metric_name = "mem.vmfs.pbc.capMissRatio.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmMemVmfsPbcOverheadLatest(BaseVSphereMetricPuller):
    """Amount of VMFS heap used by the VMFS PB Cache"""
    metric_group = "vm"
    metric_name = "mem.vmfs.pbc.overhead.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmfsPbcSizeLatest(BaseVSphereMetricPuller):
    """Space used for holding VMFS Pointer Blocks in memory"""
    metric_group = "vm"
    metric_name = "mem.vmfs.pbc.size.latest"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmMemVmfsPbcSizeMaxLatest(BaseVSphereMetricPuller):
    """Maximum size the VMFS Pointer Block Cache can grow to"""
    metric_group = "vm"
    metric_name = "mem.vmfs.pbc.sizeMax.latest"
    metric_type = "cumulative"
    metric_unit = "MB"
    pulling_interval = 10


class VSphereVmMemVmfsPbcWorkingSetLatest(BaseVSphereMetricPuller):
    """Amount of file blocks whose addresses are cached in the VMFS PB Cache"""
    metric_group = "vm"
    metric_name = "mem.vmfs.pbc.workingSet.latest"
    metric_type = "cumulative"
    metric_unit = "TB"
    pulling_interval = 10


class VSphereVmMemVmfsPbcWorkingSetMaxLatest(BaseVSphereMetricPuller):
    """Maximum amount of file blocks whose addresses are cached in the VMFS PB
    Cache
    """
    metric_group = "vm"
    metric_name = "mem.vmfs.pbc.workingSetMax.latest"
    metric_type = "cumulative"
    metric_unit = "TB"
    pulling_interval = 10


class VSphereVmMemVmmemctl(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctl"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctlAverage(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctl.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctlMaximum(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctl.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctlMinimum(BaseVSphereMetricPuller):
    """Amount of memory allocated by the virtual machine memory control driver
    (vmmemctl), which is installed with VMware Tools
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctl.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctltarget(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctltarget"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctltargetAverage(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctltarget.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctltargetMaximum(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctltarget.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemVmmemctltargetMinimum(BaseVSphereMetricPuller):
    """Target value set by VMkernal for the virtual machine's memory balloon
    size
    """
    metric_group = "vm"
    metric_name = "mem.vmmemctltarget.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemZero(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "vm"
    metric_name = "mem.zero"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemZeroAverage(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "vm"
    metric_name = "mem.zero.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemZeroMaximum(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "vm"
    metric_name = "mem.zero.maximum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemZeroMinimum(BaseVSphereMetricPuller):
    """Memory that contains 0s only"""
    metric_group = "vm"
    metric_name = "mem.zero.minimum"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemZipSavedLatest(BaseVSphereMetricPuller):
    """Memory (KB) saved due to memory zipping"""
    metric_group = "vm"
    metric_name = "mem.zipSaved.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmMemZippedLatest(BaseVSphereMetricPuller):
    """Memory (KB) zipped"""
    metric_group = "vm"
    metric_name = "mem.zipped.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmNetBroadcastRxSummation(BaseVSphereMetricPuller):
    """Number of broadcast packets received during the sampling interval"""
    metric_group = "vm"
    metric_name = "net.broadcastRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetBroadcastTxSummation(BaseVSphereMetricPuller):
    """Number of broadcast packets transmitted during the sampling interval"""
    metric_group = "vm"
    metric_name = "net.broadcastTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetBytesRxAverage(BaseVSphereMetricPuller):
    """Average amount of data received per second"""
    metric_group = "vm"
    metric_name = "net.bytesRx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetBytesTxAverage(BaseVSphereMetricPuller):
    """Average amount of data transmitted per second"""
    metric_group = "vm"
    metric_name = "net.bytesTx.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetDroppedRxSummation(BaseVSphereMetricPuller):
    """Number of receives dropped"""
    metric_group = "vm"
    metric_name = "net.droppedRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetDroppedTxSummation(BaseVSphereMetricPuller):
    """Number of transmits dropped"""
    metric_group = "vm"
    metric_name = "net.droppedTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetErrorsRxSummation(BaseVSphereMetricPuller):
    """Number of packets with errors received during the sampling interval"""
    metric_group = "vm"
    metric_name = "net.errorsRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetErrorsTxSummation(BaseVSphereMetricPuller):
    """Number of packets with errors transmitted during the sampling
    interval
    """
    metric_group = "vm"
    metric_name = "net.errorsTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetMulticastRxSummation(BaseVSphereMetricPuller):
    """Number of multicast packets received during the sampling interval"""
    metric_group = "vm"
    metric_name = "net.multicastRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetMulticastTxSummation(BaseVSphereMetricPuller):
    """Number of multicast packets transmitted during the sampling interval"""
    metric_group = "vm"
    metric_name = "net.multicastTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetPacketsRxSummation(BaseVSphereMetricPuller):
    """Number of packets received during the interval"""
    metric_group = "vm"
    metric_name = "net.packetsRx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetPacketsTxSummation(BaseVSphereMetricPuller):
    """Number of packets transmitted during the interval"""
    metric_group = "vm"
    metric_name = "net.packetsTx.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetReceivedAverage(BaseVSphereMetricPuller):
    """Average rate at which data was received during the interval"""
    metric_group = "vm"
    metric_name = "net.received.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputContentionSummation(BaseVSphereMetricPuller):
    """The aggregate network droppped packets for the host"""
    metric_group = "vm"
    metric_name = "net.throughput.contention.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputDroppedRxAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.droppedRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputDroppedTxAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.droppedTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPacketsPerSecAverage(BaseVSphereMetricPuller):
    """Average rate of packets received and transmitted per second"""
    metric_group = "vm"
    metric_name = "net.throughput.packetsPerSec.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPktsRxAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this vDS"""
    metric_group = "vm"
    metric_name = "net.throughput.pktsRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPktsRxBroadcastAverage(BaseVSphereMetricPuller):
    """The rate of received Broadcast packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.pktsRxBroadcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPktsRxMulticastAverage(BaseVSphereMetricPuller):
    """The rate of received Multicast packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.pktsRxMulticast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPktsTxAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.pktsTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPktsTxBroadcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Broadcast packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.pktsTxBroadcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputPktsTxMulticastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Multicast packets for this VDS"""
    metric_group = "vm"
    metric_name = "net.throughput.pktsTxMulticast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputProvisionedAverage(BaseVSphereMetricPuller):
    """The maximum network bandwidth for the host"""
    metric_group = "vm"
    metric_name = "net.throughput.provisioned.average"
    metric_type = "cumulative"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsableAverage(BaseVSphereMetricPuller):
    """The current available network bandwidth for the host"""
    metric_group = "vm"
    metric_name = "net.throughput.usable.average"
    metric_type = "cumulative"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageAverage(BaseVSphereMetricPuller):
    """The current network bandwidth usage for the host"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageFtAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for FT"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.ft.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageHbrAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for HBR"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.hbr.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageIscsiAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for iSCSI"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.iscsi.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageNfsAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for NFS"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.nfs.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageVmAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for VMs"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.vm.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputUsageVmotionAverage(BaseVSphereMetricPuller):
    """Average pNic I/O rate for vMotion"""
    metric_group = "vm"
    metric_name = "net.throughput.usage.vmotion.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpFoundAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that found matched ARP entry for this
    network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpFound.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpFoundSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that found matched ARP entry for this
    network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpFound.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpLKUPFullAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new ARP entry
    during translation phase for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpLKUPFull.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpLKUPFullSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new ARP entry
    during translation phase for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpLKUPFull.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpTimeoutAverage(BaseVSphereMetricPuller):
    """Count of arp queries that have been expired for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpTimeout.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpTimeoutSummation(BaseVSphereMetricPuller):
    """Count of arp queries that have been expired for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpTimeout.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpUnknownAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets whose matched arp entry is marked as
    unknown for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpUnknown.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpUnknownSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets whose matched arp entry is marked as
    unknown for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpUnknown.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpWaitAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets whose ARP requests have already been sent
    into queue for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpWait.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsArpWaitSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets whose ARP requests have already been sent
    into queue for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.arpWait.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsDroppedRxAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.droppedRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsDroppedTxAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.droppedTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagDropRxAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagDropRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagDropTxAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagDropTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagRxAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagRxBcastAverage(BaseVSphereMetricPuller):
    """The rate of received Broadcast packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagRxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagRxMcastAverage(BaseVSphereMetricPuller):
    """The rate of received multicast packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagRxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagTxAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagTxBcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Broadcast packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagTxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsLagTxMcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted Multicast packets for this LAG"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.lagTxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsMacFloodAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that cannot find matched mapping entry for
    this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.macFlood.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsMacFloodSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that cannot find matched mapping entry for
    this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.macFlood.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsMacLKUPFullAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during translation phase for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.macLKUPFull.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsMacLKUPFullSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during translation phase for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.macLKUPFull.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsMacUPDTFullAverage(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during learning phase for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.macUPDTFull.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsMacUPDTFullSummation(BaseVSphereMetricPuller):
    """Count of transmitted packets that failed to acquire new mapping entry
    during learning phase for this network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.macUPDTFull.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsPktsRxAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.pktsRx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsPktsRxBcastAverage(BaseVSphereMetricPuller):
    """The rate of received broadcast packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.pktsRxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsPktsRxMcastAverage(BaseVSphereMetricPuller):
    """The rate of received multicast packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.pktsRxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsPktsTxAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.pktsTx.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsPktsTxBcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted broadcast packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.pktsTxBcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsPktsTxMcastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted multicast packets for this DVPort"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.pktsTxMcast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsRxDestErrAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets with destination IP error for this
    network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.rxDestErr.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsRxDestErrSummation(BaseVSphereMetricPuller):
    """Count of dropped received packets with destination IP error for this
    network
    """
    metric_group = "vm"
    metric_name = "net.throughput.vds.rxDestErr.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsRxDropAverage(BaseVSphereMetricPuller):
    """Count of dropped received packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.rxDrop.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsRxDropSummation(BaseVSphereMetricPuller):
    """Count of dropped received packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.rxDrop.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsRxTotalAverage(BaseVSphereMetricPuller):
    """The rate of received packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.rxTotal.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsRxTotalSummation(BaseVSphereMetricPuller):
    """The rate of received packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.rxTotal.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxCrsRouterAverage(BaseVSphereMetricPuller):
    """The rate of transmitted cross-router packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txCrsRouter.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxCrsRouterSummation(BaseVSphereMetricPuller):
    """The rate of transmitted cross-router packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txCrsRouter.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxDropAverage(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txDrop.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxDropSummation(BaseVSphereMetricPuller):
    """Count of dropped transmitted packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txDrop.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxNoUnicastAverage(BaseVSphereMetricPuller):
    """The rate of transmitted non-unicast packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txNoUnicast.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxNoUnicastSummation(BaseVSphereMetricPuller):
    """The rate of transmitted non-unicast packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txNoUnicast.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxTotalAverage(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txTotal.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetThroughputVdsTxTotalSummation(BaseVSphereMetricPuller):
    """The rate of transmitted packets for this network"""
    metric_group = "vm"
    metric_name = "net.throughput.vds.txTotal.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetTransmittedAverage(BaseVSphereMetricPuller):
    """Average rate at which data was transmitted during the interval"""
    metric_group = "vm"
    metric_name = "net.transmitted.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetUnknownProtosSummation(BaseVSphereMetricPuller):
    """Number of frames with unknown protocol received during the sampling
    interval
    """
    metric_group = "vm"
    metric_name = "net.unknownProtos.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmNetUsage(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "vm"
    metric_name = "net.usage"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetUsageAverage(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "vm"
    metric_name = "net.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetUsageMaximum(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "vm"
    metric_name = "net.usage.maximum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmNetUsageMinimum(BaseVSphereMetricPuller):
    """Network utilization (combined transmit-rates and receive-rates) during
    the interval
    """
    metric_group = "vm"
    metric_name = "net.usage.minimum"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmPowerCapacityUsableAverage(BaseVSphereMetricPuller):
    """Current maximum allowed power usage."""
    metric_group = "vm"
    metric_name = "power.capacity.usable.average"
    metric_type = "cumulative"
    metric_unit = "W"
    pulling_interval = 10


class VSphereVmPowerCapacityUsageAverage(BaseVSphereMetricPuller):
    """Current power usage"""
    metric_group = "vm"
    metric_name = "power.capacity.usage.average"
    metric_type = "cumulative"
    metric_unit = "W"
    pulling_interval = 10


class VSphereVmPowerCapacityUsagePctAverage(BaseVSphereMetricPuller):
    """Current power usage as a percentage of maximum allowed power."""
    metric_group = "vm"
    metric_name = "power.capacity.usagePct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmPowerEnergySummation(BaseVSphereMetricPuller):
    """Total energy used since last stats reset"""
    metric_group = "vm"
    metric_name = "power.energy.summation"
    metric_type = "delta"
    metric_unit = "J"
    pulling_interval = 10


class VSphereVmPowerPowerAverage(BaseVSphereMetricPuller):
    """Current power usage"""
    metric_group = "vm"
    metric_name = "power.power.average"
    metric_type = "gauge"
    metric_unit = "W"
    pulling_interval = 10


class VSphereVmPowerPowerCapAverage(BaseVSphereMetricPuller):
    """Maximum allowed power usage"""
    metric_group = "vm"
    metric_name = "power.powerCap.average"
    metric_type = "cumulative"
    metric_unit = "W"
    pulling_interval = 10


class VSphereVmRescpuActav1Latest(BaseVSphereMetricPuller):
    """CPU active average over 1 minute"""
    metric_group = "vm"
    metric_name = "rescpu.actav1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuActav15Latest(BaseVSphereMetricPuller):
    """CPU active average over 15 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.actav15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuActav5Latest(BaseVSphereMetricPuller):
    """CPU active average over 5 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.actav5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuActpk1Latest(BaseVSphereMetricPuller):
    """CPU active peak over 1 minute"""
    metric_group = "vm"
    metric_name = "rescpu.actpk1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuActpk15Latest(BaseVSphereMetricPuller):
    """CPU active peak over 15 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.actpk15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuActpk5Latest(BaseVSphereMetricPuller):
    """CPU active peak over 5 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.actpk5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuMaxLimited1Latest(BaseVSphereMetricPuller):
    """Amount of CPU resources over the limit that were refused, average over
    1 minute
    """
    metric_group = "vm"
    metric_name = "rescpu.maxLimited1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuMaxLimited15Latest(BaseVSphereMetricPuller):
    """Amount of CPU resources over the limit that were refused, average over
    15 minutes
    """
    metric_group = "vm"
    metric_name = "rescpu.maxLimited15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuMaxLimited5Latest(BaseVSphereMetricPuller):
    """Amount of CPU resources over the limit that were refused, average over
    5 minutes
    """
    metric_group = "vm"
    metric_name = "rescpu.maxLimited5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuRunav1Latest(BaseVSphereMetricPuller):
    """CPU running average over 1 minute"""
    metric_group = "vm"
    metric_name = "rescpu.runav1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuRunav15Latest(BaseVSphereMetricPuller):
    """CPU running average over 15 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.runav15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuRunav5Latest(BaseVSphereMetricPuller):
    """CPU running average over 5 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.runav5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuRunpk1Latest(BaseVSphereMetricPuller):
    """CPU running peak over 1 minute"""
    metric_group = "vm"
    metric_name = "rescpu.runpk1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuRunpk15Latest(BaseVSphereMetricPuller):
    """CPU running peak over 15 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.runpk15.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuRunpk5Latest(BaseVSphereMetricPuller):
    """CPU running peak over 5 minutes"""
    metric_group = "vm"
    metric_name = "rescpu.runpk5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmRescpuSampleCountLatest(BaseVSphereMetricPuller):
    """Group CPU sample count"""
    metric_group = "vm"
    metric_name = "rescpu.sampleCount.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmRescpuSamplePeriodLatest(BaseVSphereMetricPuller):
    """Group CPU sample period"""
    metric_group = "vm"
    metric_name = "rescpu.samplePeriod.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStorageAdapterOIOsPctAverage(BaseVSphereMetricPuller):
    """The percent of I/Os that have been issued but have not yet completed"""
    metric_group = "vm"
    metric_name = "storageAdapter.OIOsPct.average"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmStorageAdapterCommandsAveragedAverage(BaseVSphereMetricPuller):
    """Average number of commands issued per second by the storage adapter
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "storageAdapter.commandsAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStorageAdapterMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all storage adapters used by the host"""
    metric_group = "vm"
    metric_name = "storageAdapter.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStorageAdapterNumberReadAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of read commands issued per second by the storage
    adapter during the collection interval
    """
    metric_group = "vm"
    metric_name = "storageAdapter.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStorageAdapterNumberWriteAveragedAverage(
        BaseVSphereMetricPuller):
    """Average number of write commands issued per second by the storage
    adapter during the collection interval
    """
    metric_group = "vm"
    metric_name = "storageAdapter.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStorageAdapterOutstandingIOsAverage(BaseVSphereMetricPuller):
    """The number of I/Os that have been issued but have not yet completed"""
    metric_group = "vm"
    metric_name = "storageAdapter.outstandingIOs.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStorageAdapterQueueDepthAverage(BaseVSphereMetricPuller):
    """The maximum number of I/Os that can be outstanding at a given time"""
    metric_group = "vm"
    metric_name = "storageAdapter.queueDepth.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStorageAdapterQueueLatencyAverage(BaseVSphereMetricPuller):
    """Average amount of time spent in the VMkernel queue, per SCSI command,
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "storageAdapter.queueLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStorageAdapterQueuedAverage(BaseVSphereMetricPuller):
    """The current number of I/Os that are waiting to be issued"""
    metric_group = "vm"
    metric_name = "storageAdapter.queued.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStorageAdapterReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data by the storage adapter"""
    metric_group = "vm"
    metric_name = "storageAdapter.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmStorageAdapterThroughputContAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "vm"
    metric_name = "storageAdapter.throughput.cont.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStorageAdapterThroughputUsagAverage(BaseVSphereMetricPuller):
    """The storage adapter's I/O rate"""
    metric_group = "vm"
    metric_name = "storageAdapter.throughput.usag.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmStorageAdapterTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read by the storage adapter takes"""
    metric_group = "vm"
    metric_name = "storageAdapter.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStorageAdapterTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write by the storage adapter takes"""
    metric_group = "vm"
    metric_name = "storageAdapter.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStorageAdapterWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data by the storage adapter"""
    metric_group = "vm"
    metric_name = "storageAdapter.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmStoragePathBusResetsSummation(BaseVSphereMetricPuller):
    """Number of SCSI-bus reset commands issued during the collection
    interval
    """
    metric_group = "vm"
    metric_name = "storagePath.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStoragePathCommandsAbortedSummation(BaseVSphereMetricPuller):
    """Number of SCSI commands terminated during the collection interval"""
    metric_group = "vm"
    metric_name = "storagePath.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStoragePathCommandsAveragedAverage(BaseVSphereMetricPuller):
    """Average number of commands issued per second on the storage path during
    the collection interval
    """
    metric_group = "vm"
    metric_name = "storagePath.commandsAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStoragePathMaxTotalLatencyLatest(BaseVSphereMetricPuller):
    """Highest latency value across all storage paths used by the host"""
    metric_group = "vm"
    metric_name = "storagePath.maxTotalLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStoragePathNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of read commands issued per second on the storage path
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "storagePath.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStoragePathNumberWriteAveragedAverage(BaseVSphereMetricPuller):
    """Average number of write commands issued per second on the storage path
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "storagePath.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmStoragePathReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data on the storage path"""
    metric_group = "vm"
    metric_name = "storagePath.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmStoragePathThroughputContAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "vm"
    metric_name = "storagePath.throughput.cont.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStoragePathThroughputUsageAverage(BaseVSphereMetricPuller):
    """Storage path I/O rate"""
    metric_group = "vm"
    metric_name = "storagePath.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmStoragePathTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read issued on the storage path takes"""
    metric_group = "vm"
    metric_name = "storagePath.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStoragePathTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write issued on the storage path takes"""
    metric_group = "vm"
    metric_name = "storagePath.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmStoragePathWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data on the storage path"""
    metric_group = "vm"
    metric_name = "storagePath.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmSysDiskUsageLatest(BaseVSphereMetricPuller):
    """Amount of disk space usage for each mount point"""
    metric_group = "vm"
    metric_name = "sys.diskUsage.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysHeartbeatLatest(BaseVSphereMetricPuller):
    """Number of heartbeats issued per virtual machine during the interval"""
    metric_group = "vm"
    metric_name = "sys.heartbeat.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmSysHeartbeatSummation(BaseVSphereMetricPuller):
    """Number of heartbeats issued per virtual machine during the interval"""
    metric_group = "vm"
    metric_name = "sys.heartbeat.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmSysOsUptimeLatest(BaseVSphereMetricPuller):
    """Total time elapsed, in seconds, since last operating system boot-up"""
    metric_group = "vm"
    metric_name = "sys.osUptime.latest"
    metric_type = "cumulative"
    metric_unit = "s"
    pulling_interval = 10


class VSphereVmSysResourceCpuAct1Latest(BaseVSphereMetricPuller):
    """CPU active average over 1 minute of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuAct1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysResourceCpuAct5Latest(BaseVSphereMetricPuller):
    """CPU active average over 5 minutes of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuAct5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysResourceCpuAllocMaxLatest(BaseVSphereMetricPuller):
    """CPU allocation limit (in MHz) of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuAllocMax.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmSysResourceCpuAllocMinLatest(BaseVSphereMetricPuller):
    """CPU allocation reservation (in MHz) of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuAllocMin.latest"
    metric_type = "cumulative"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmSysResourceCpuAllocSharesLatest(BaseVSphereMetricPuller):
    """CPU allocation shares of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuAllocShares.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmSysResourceCpuMaxLimited1Latest(BaseVSphereMetricPuller):
    """CPU maximum limited over 1 minute of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuMaxLimited1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysResourceCpuMaxLimited5Latest(BaseVSphereMetricPuller):
    """CPU maximum limited over 5 minutes of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuMaxLimited5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysResourceCpuRun1Latest(BaseVSphereMetricPuller):
    """CPU running average over 1 minute of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuRun1.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysResourceCpuRun5Latest(BaseVSphereMetricPuller):
    """CPU running average over 5 minutes of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceCpuRun5.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmSysResourceCpuUsage(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "vm"
    metric_name = "sys.resourceCpuUsage"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmSysResourceCpuUsageAverage(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "vm"
    metric_name = "sys.resourceCpuUsage.average"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmSysResourceCpuUsageMaximum(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "vm"
    metric_name = "sys.resourceCpuUsage.maximum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmSysResourceCpuUsageMinimum(BaseVSphereMetricPuller):
    """Amount of CPU used by the Service Console and other applications during
    the interval
    """
    metric_group = "vm"
    metric_name = "sys.resourceCpuUsage.minimum"
    metric_type = "gauge"
    metric_unit = "MHz"
    pulling_interval = 10


class VSphereVmSysResourceFdUsageLatest(BaseVSphereMetricPuller):
    """Number of file descriptors used by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceFdUsage.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmSysResourceMemAllocMaxLatest(BaseVSphereMetricPuller):
    """Memory allocation limit (in KB) of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemAllocMax.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemAllocMinLatest(BaseVSphereMetricPuller):
    """Memory allocation reservation (in KB) of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemAllocMin.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemAllocSharesLatest(BaseVSphereMetricPuller):
    """Memory allocation shares of the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemAllocShares.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmSysResourceMemConsumedLatest(BaseVSphereMetricPuller):
    """Memory consumed by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemConsumed.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemCowLatest(BaseVSphereMetricPuller):
    """Memory shared by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemCow.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemMappedLatest(BaseVSphereMetricPuller):
    """Memory mapped by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemMapped.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemOverheadLatest(BaseVSphereMetricPuller):
    """Overhead memory consumed by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemOverhead.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemSharedLatest(BaseVSphereMetricPuller):
    """Memory saved due to sharing by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemShared.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemSwappedLatest(BaseVSphereMetricPuller):
    """Memory swapped out by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemSwapped.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemTouchedLatest(BaseVSphereMetricPuller):
    """Memory touched by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemTouched.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysResourceMemZeroLatest(BaseVSphereMetricPuller):
    """Zero filled memory used by the system resource group"""
    metric_group = "vm"
    metric_name = "sys.resourceMemZero.latest"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmSysUptimeLatest(BaseVSphereMetricPuller):
    """Total time elapsed, in seconds, since last system startup"""
    metric_group = "vm"
    metric_name = "sys.uptime.latest"
    metric_type = "cumulative"
    metric_unit = "s"
    pulling_interval = 10


class VSphereVmVcDebugInfoActivationlatencystatsMaximum(
        BaseVSphereMetricPuller):
    """The latency of an activation operation in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.activationlatencystats.maximum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVcDebugInfoActivationlatencystatsMinimum(
        BaseVSphereMetricPuller):
    """The latency of an activation operation in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.activationlatencystats.minimum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVcDebugInfoActivationlatencystatsSummation(
        BaseVSphereMetricPuller):
    """The latency of an activation operation in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.activationlatencystats.summation"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVcDebugInfoActivationstatsMaximum(BaseVSphereMetricPuller):
    """Activation operations in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.activationstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoActivationstatsMinimum(BaseVSphereMetricPuller):
    """Activation operations in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.activationstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoActivationstatsSummation(BaseVSphereMetricPuller):
    """Activation operations in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.activationstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoHostsynclatencystatsMaximum(BaseVSphereMetricPuller):
    """The latency of a host sync operation in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.hostsynclatencystats.maximum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVcDebugInfoHostsynclatencystatsMinimum(BaseVSphereMetricPuller):
    """The latency of a host sync operation in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.hostsynclatencystats.minimum"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVcDebugInfoHostsynclatencystatsSummation(
        BaseVSphereMetricPuller):
    """The latency of a host sync operation in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.hostsynclatencystats.summation"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVcDebugInfoHostsyncstatsMaximum(BaseVSphereMetricPuller):
    """The number of host sync operations in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.hostsyncstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoHostsyncstatsMinimum(BaseVSphereMetricPuller):
    """The number of host sync operations in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.hostsyncstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoHostsyncstatsSummation(BaseVSphereMetricPuller):
    """The number of host sync operations in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.hostsyncstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoInventorystatsMaximum(BaseVSphereMetricPuller):
    """vCenter Server inventory statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.inventorystats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoInventorystatsMinimum(BaseVSphereMetricPuller):
    """vCenter Server inventory statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.inventorystats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoInventorystatsSummation(BaseVSphereMetricPuller):
    """vCenter Server inventory statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.inventorystats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoLockstatsMaximum(BaseVSphereMetricPuller):
    """vCenter Server locking statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.lockstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoLockstatsMinimum(BaseVSphereMetricPuller):
    """vCenter Server locking statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.lockstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoLockstatsSummation(BaseVSphereMetricPuller):
    """vCenter Server locking statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.lockstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoLrostatsMaximum(BaseVSphereMetricPuller):
    """vCenter Server LRO statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.lrostats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoLrostatsMinimum(BaseVSphereMetricPuller):
    """vCenter Server LRO statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.lrostats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoLrostatsSummation(BaseVSphereMetricPuller):
    """vCenter Server LRO statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.lrostats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoMiscstatsMaximum(BaseVSphereMetricPuller):
    """Miscellaneous statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.miscstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoMiscstatsMinimum(BaseVSphereMetricPuller):
    """Miscellaneous statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.miscstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoMiscstatsSummation(BaseVSphereMetricPuller):
    """Miscellaneous statistics"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.miscstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoMorefregstatsMaximum(BaseVSphereMetricPuller):
    """Managed object reference counts in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.morefregstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoMorefregstatsMinimum(BaseVSphereMetricPuller):
    """Managed object reference counts in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.morefregstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoMorefregstatsSummation(BaseVSphereMetricPuller):
    """Managed object reference counts in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.morefregstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoScoreboardMaximum(BaseVSphereMetricPuller):
    """Object counts in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.scoreboard.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoScoreboardMinimum(BaseVSphereMetricPuller):
    """Object counts in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.scoreboard.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoScoreboardSummation(BaseVSphereMetricPuller):
    """Object counts in vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.scoreboard.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoSessionstatsMaximum(BaseVSphereMetricPuller):
    """The statistics of client sessions connected to vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.sessionstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoSessionstatsMinimum(BaseVSphereMetricPuller):
    """The statistics of client sessions connected to vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.sessionstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoSessionstatsSummation(BaseVSphereMetricPuller):
    """The statistics of client sessions connected to vCenter Server"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.sessionstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoSystemstatsMaximum(BaseVSphereMetricPuller):
    """The statistics of vCenter Server as a running system such as thread
    statistics and heap statistics
    """
    metric_group = "vm"
    metric_name = "vcDebugInfo.systemstats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoSystemstatsMinimum(BaseVSphereMetricPuller):
    """The statistics of vCenter Server as a running system such as thread
    statistics and heap statistics
    """
    metric_group = "vm"
    metric_name = "vcDebugInfo.systemstats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoSystemstatsSummation(BaseVSphereMetricPuller):
    """The statistics of vCenter Server as a running system such as thread
    statistics and heap statistics
    """
    metric_group = "vm"
    metric_name = "vcDebugInfo.systemstats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoVcservicestatsMaximum(BaseVSphereMetricPuller):
    """vCenter service statistics such as events, alarms, and tasks"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.vcservicestats.maximum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoVcservicestatsMinimum(BaseVSphereMetricPuller):
    """vCenter service statistics such as events, alarms, and tasks"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.vcservicestats.minimum"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcDebugInfoVcservicestatsSummation(BaseVSphereMetricPuller):
    """vCenter service statistics such as events, alarms, and tasks"""
    metric_group = "vm"
    metric_name = "vcDebugInfo.vcservicestats.summation"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesCpuqueuelengthAverage(BaseVSphereMetricPuller):
    """Processor queue length on the system where vCenter Server is running"""
    metric_group = "vm"
    metric_name = "vcResources.cpuqueuelength.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesCtxswitchesrateAverage(BaseVSphereMetricPuller):
    """Number of context switches per second on the system where vCenter
    Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.ctxswitchesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesDiskqueuelengthAverage(BaseVSphereMetricPuller):
    """Disk queue length on the system where vCenter Server is running"""
    metric_group = "vm"
    metric_name = "vcResources.diskqueuelength.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesDiskreadbytesrateAverage(BaseVSphereMetricPuller):
    """Number of bytes read from the disk per second on the system where
    vCenter Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.diskreadbytesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesDiskreadsrateAverage(BaseVSphereMetricPuller):
    """Number of disk reads per second on the system where vCenter Server is
    running
    """
    metric_group = "vm"
    metric_name = "vcResources.diskreadsrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesDiskwritebytesrateAverage(BaseVSphereMetricPuller):
    """Number of bytes written to the disk per second on the system where
    vCenter Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.diskwritebytesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesDiskwritesrateAverage(BaseVSphereMetricPuller):
    """Number of disk writes per second on the system where vCenter Server is
    running
    """
    metric_group = "vm"
    metric_name = "vcResources.diskwritesrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesNetqueuelengthAverage(BaseVSphereMetricPuller):
    """Network queue length on the system where vCenter Server is running"""
    metric_group = "vm"
    metric_name = "vcResources.netqueuelength.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesPacketrateAverage(BaseVSphereMetricPuller):
    """Number of total packets sent and received per second on the system
    where vCenter Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.packetrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesPacketrecvrateAverage(BaseVSphereMetricPuller):
    """Rate of the number of total packets received per second on the system
    where vCenter Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.packetrecvrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesPacketsentrateAverage(BaseVSphereMetricPuller):
    """Number of total packets sent per second on the system where vCenter
    Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.packetsentrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesPagefaultrateAverage(BaseVSphereMetricPuller):
    """Number of page faults per second on the system where vCenter Server is
    running
    """
    metric_group = "vm"
    metric_name = "vcResources.pagefaultrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesPhysicalmemusageAverage(BaseVSphereMetricPuller):
    """Physical memory used by vCenter"""
    metric_group = "vm"
    metric_name = "vcResources.physicalmemusage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmVcResourcesPoolnonpagedbytesAverage(BaseVSphereMetricPuller):
    """Memory pooled for non-paged bytes on the system where vCenter Server is
    running
    """
    metric_group = "vm"
    metric_name = "vcResources.poolnonpagedbytes.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmVcResourcesPoolpagedbytesAverage(BaseVSphereMetricPuller):
    """Memory pooled for paged bytes on the system where vCenter Server is
    running
    """
    metric_group = "vm"
    metric_name = "vcResources.poolpagedbytes.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmVcResourcesPriviledgedcpuusageAverage(BaseVSphereMetricPuller):
    """CPU used by vCenter Server in privileged mode"""
    metric_group = "vm"
    metric_name = "vcResources.priviledgedcpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmVcResourcesProcesscpuusageAverage(BaseVSphereMetricPuller):
    """Total CPU used by vCenter Server"""
    metric_group = "vm"
    metric_name = "vcResources.processcpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmVcResourcesProcesshandlesAverage(BaseVSphereMetricPuller):
    """Handles used by vCenter Server"""
    metric_group = "vm"
    metric_name = "vcResources.processhandles.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesProcessthreadsAverage(BaseVSphereMetricPuller):
    """Number of threads used by vCenter Server"""
    metric_group = "vm"
    metric_name = "vcResources.processthreads.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesSyscallsrateAverage(BaseVSphereMetricPuller):
    """Number of systems calls made per second on the system where vCenter
    Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.syscallsrate.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesSystemcpuusageAverage(BaseVSphereMetricPuller):
    """Total system CPU used on the system where vCenter Server in running"""
    metric_group = "vm"
    metric_name = "vcResources.systemcpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmVcResourcesSystemnetusageAverage(BaseVSphereMetricPuller):
    """Total network bytes received and sent per second on the system where
    vCenter Server is running
    """
    metric_group = "vm"
    metric_name = "vcResources.systemnetusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmVcResourcesSystemthreadsAverage(BaseVSphereMetricPuller):
    """Number of threads on the system where vCenter Server is running"""
    metric_group = "vm"
    metric_name = "vcResources.systemthreads.average"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVcResourcesUsercpuusageAverage(BaseVSphereMetricPuller):
    """CPU used by vCenter Server in user mode"""
    metric_group = "vm"
    metric_name = "vcResources.usercpuusage.average"
    metric_type = "gauge"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmVcResourcesVirtualmemusageAverage(BaseVSphereMetricPuller):
    """Virtual memory used by vCenter Server"""
    metric_group = "vm"
    metric_name = "vcResources.virtualmemusage.average"
    metric_type = "cumulative"
    metric_unit = "KB"
    pulling_interval = 10


class VSphereVmVflashModuleNumActiveVMDKsLatest(BaseVSphereMetricPuller):
    """Number of caches controlled by the virtual flash module"""
    metric_group = "vm"
    metric_name = "vflashModule.numActiveVMDKs.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskBusResetsSummation(BaseVSphereMetricPuller):
    """Number of resets to a virtual disk"""
    metric_group = "vm"
    metric_name = "virtualDisk.busResets.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskCommandsAbortedSummation(BaseVSphereMetricPuller):
    """Number of terminations to a virtual disk"""
    metric_group = "vm"
    metric_name = "virtualDisk.commandsAborted.summation"
    metric_type = "delta"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskLargeSeeksLatest(BaseVSphereMetricPuller):
    """Number of seeks during the interval that were greater than 8192 LBNs
    apart
    """
    metric_group = "vm"
    metric_name = "virtualDisk.largeSeeks.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskMediumSeeksLatest(BaseVSphereMetricPuller):
    """Number of seeks during the interval that were between 64 and 8192 LBNs
    apart
    """
    metric_group = "vm"
    metric_name = "virtualDisk.mediumSeeks.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskNumberReadAveragedAverage(BaseVSphereMetricPuller):
    """Average number of read commands issued per second to the virtual disk
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "virtualDisk.numberReadAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskNumberWriteAveragedAverage(BaseVSphereMetricPuller):
    """Average number of write commands issued per second to the virtual disk
    during the collection interval
    """
    metric_group = "vm"
    metric_name = "virtualDisk.numberWriteAveraged.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskReadAverage(BaseVSphereMetricPuller):
    """Rate of reading data from the virtual disk"""
    metric_group = "vm"
    metric_name = "virtualDisk.read.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmVirtualDiskReadIOSizeLatest(BaseVSphereMetricPuller):
    """Average read request size in bytes"""
    metric_group = "vm"
    metric_name = "virtualDisk.readIOSize.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskReadLatencyUSLatest(BaseVSphereMetricPuller):
    """Read latency in microseconds"""
    metric_group = "vm"
    metric_name = "virtualDisk.readLatencyUS.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereVmVirtualDiskReadLoadMetricLatest(BaseVSphereMetricPuller):
    """Storage DRS virtual disk metric for the read workload model"""
    metric_group = "vm"
    metric_name = "virtualDisk.readLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskReadOIOLatest(BaseVSphereMetricPuller):
    """Average number of outstanding read requests to the virtual disk during
    the collection interval
    """
    metric_group = "vm"
    metric_name = "virtualDisk.readOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskSmallSeeksLatest(BaseVSphereMetricPuller):
    """Number of seeks during the interval that were less than 64 LBNs apart"""
    metric_group = "vm"
    metric_name = "virtualDisk.smallSeeks.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskThroughputContAverage(BaseVSphereMetricPuller):
    """Average amount of time for an I/O operation to complete successfully"""
    metric_group = "vm"
    metric_name = "virtualDisk.throughput.cont.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVirtualDiskThroughputUsageAverage(BaseVSphereMetricPuller):
    """Virtual disk I/O rate"""
    metric_group = "vm"
    metric_name = "virtualDisk.throughput.usage.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmVirtualDiskTotalReadLatencyAverage(BaseVSphereMetricPuller):
    """The average time a read from the virtual disk takes"""
    metric_group = "vm"
    metric_name = "virtualDisk.totalReadLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVirtualDiskTotalWriteLatencyAverage(BaseVSphereMetricPuller):
    """The average time a write to the virtual disk takes"""
    metric_group = "vm"
    metric_name = "virtualDisk.totalWriteLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVirtualDiskVFlashCacheIopsLatest(BaseVSphereMetricPuller):
    """The average virtual Flash Read Cache I/Os per second value for the
    virtual disk
    """
    metric_group = "vm"
    metric_name = "virtualDisk.vFlashCacheIops.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskVFlashCacheLatencyLatest(BaseVSphereMetricPuller):
    """The average virtual Flash Read Cache latency value for the virtual
    disk
    """
    metric_group = "vm"
    metric_name = "virtualDisk.vFlashCacheLatency.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereVmVirtualDiskVFlashCacheThroughputLatest(BaseVSphereMetricPuller):
    """The average virtual Flash Read Cache throughput value for the virtual
    disk
    """
    metric_group = "vm"
    metric_name = "virtualDisk.vFlashCacheThroughput.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskWriteAverage(BaseVSphereMetricPuller):
    """Rate of writing data to the virtual disk"""
    metric_group = "vm"
    metric_name = "virtualDisk.write.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmVirtualDiskWriteIOSizeLatest(BaseVSphereMetricPuller):
    """Average write request size in bytes"""
    metric_group = "vm"
    metric_name = "virtualDisk.writeIOSize.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskWriteLatencyUSLatest(BaseVSphereMetricPuller):
    """Write latency in microseconds"""
    metric_group = "vm"
    metric_name = "virtualDisk.writeLatencyUS.latest"
    metric_type = "cumulative"
    metric_unit = "µs"
    pulling_interval = 10


class VSphereVmVirtualDiskWriteLoadMetricLatest(BaseVSphereMetricPuller):
    """Storage DRS virtual disk metric for the write workload model"""
    metric_group = "vm"
    metric_name = "virtualDisk.writeLoadMetric.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVirtualDiskWriteOIOLatest(BaseVSphereMetricPuller):
    """Average number of outstanding write requests to the virtual disk during
    the collection interval
    """
    metric_group = "vm"
    metric_name = "virtualDisk.writeOIO.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumChangeDSLatest(BaseVSphereMetricPuller):
    """Number of datastore change operations for powered-off and suspended
    virtual machines
    """
    metric_group = "vm"
    metric_name = "vmop.numChangeDS.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumChangeHostLatest(BaseVSphereMetricPuller):
    """Number of host change operations for powered-off and suspended VMs"""
    metric_group = "vm"
    metric_name = "vmop.numChangeHost.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumChangeHostDSLatest(BaseVSphereMetricPuller):
    """Number of host and datastore change operations for powered-off and
    suspended virtual machines
    """
    metric_group = "vm"
    metric_name = "vmop.numChangeHostDS.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumCloneLatest(BaseVSphereMetricPuller):
    """Number of virtual machine clone operations"""
    metric_group = "vm"
    metric_name = "vmop.numClone.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumCreateLatest(BaseVSphereMetricPuller):
    """Number of virtual machine create operations"""
    metric_group = "vm"
    metric_name = "vmop.numCreate.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumDeployLatest(BaseVSphereMetricPuller):
    """Number of virtual machine template deploy operations"""
    metric_group = "vm"
    metric_name = "vmop.numDeploy.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumDestroyLatest(BaseVSphereMetricPuller):
    """Number of virtual machine delete operations"""
    metric_group = "vm"
    metric_name = "vmop.numDestroy.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumPoweroffLatest(BaseVSphereMetricPuller):
    """Number of virtual machine power off operations"""
    metric_group = "vm"
    metric_name = "vmop.numPoweroff.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumPoweronLatest(BaseVSphereMetricPuller):
    """Number of virtual machine power on operations"""
    metric_group = "vm"
    metric_name = "vmop.numPoweron.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumRebootGuestLatest(BaseVSphereMetricPuller):
    """Number of virtual machine guest reboot operations"""
    metric_group = "vm"
    metric_name = "vmop.numRebootGuest.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumReconfigureLatest(BaseVSphereMetricPuller):
    """Number of virtual machine reconfigure operations"""
    metric_group = "vm"
    metric_name = "vmop.numReconfigure.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumRegisterLatest(BaseVSphereMetricPuller):
    """Number of virtual machine register operations"""
    metric_group = "vm"
    metric_name = "vmop.numRegister.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumResetLatest(BaseVSphereMetricPuller):
    """Number of virtual machine reset operations"""
    metric_group = "vm"
    metric_name = "vmop.numReset.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumSVMotionLatest(BaseVSphereMetricPuller):
    """Number of migrations with Storage vMotion (datastore change operations
    for powered-on VMs)
    """
    metric_group = "vm"
    metric_name = "vmop.numSVMotion.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumShutdownGuestLatest(BaseVSphereMetricPuller):
    """Number of virtual machine guest shutdown operations"""
    metric_group = "vm"
    metric_name = "vmop.numShutdownGuest.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumStandbyGuestLatest(BaseVSphereMetricPuller):
    """Number of virtual machine standby guest operations"""
    metric_group = "vm"
    metric_name = "vmop.numStandbyGuest.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumSuspendLatest(BaseVSphereMetricPuller):
    """Number of virtual machine suspend operations"""
    metric_group = "vm"
    metric_name = "vmop.numSuspend.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumUnregisterLatest(BaseVSphereMetricPuller):
    """Number of virtual machine unregister operations"""
    metric_group = "vm"
    metric_name = "vmop.numUnregister.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumVMotionLatest(BaseVSphereMetricPuller):
    """Number of migrations with vMotion (host change operations for
    powered-on VMs)
    """
    metric_group = "vm"
    metric_name = "vmop.numVMotion.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVmopNumXVMotionLatest(BaseVSphereMetricPuller):
    """Number of host and datastore change operations for powered-on and
    suspended virtual machines
    """
    metric_group = "vm"
    metric_name = "vmop.numXVMotion.latest"
    metric_type = "cumulative"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjReadAvgLatencyAverage(BaseVSphereMetricPuller):
    """Average read latency in ms"""
    metric_group = "vm"
    metric_name = "vsanDomObj.readAvgLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVsanDomObjReadCacheHitRateLatest(BaseVSphereMetricPuller):
    """Cache hit rate percentage"""
    metric_group = "vm"
    metric_name = "vsanDomObj.readCacheHitRate.latest"
    metric_type = "cumulative"
    metric_unit = "%"
    pulling_interval = 10


class VSphereVmVsanDomObjReadCongestionAverage(BaseVSphereMetricPuller):
    """Read congestion"""
    metric_group = "vm"
    metric_name = "vsanDomObj.readCongestion.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjReadIopsAverage(BaseVSphereMetricPuller):
    """Read IOPS"""
    metric_group = "vm"
    metric_name = "vsanDomObj.readIops.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjReadMaxLatencyLatest(BaseVSphereMetricPuller):
    """Max read latency in ms"""
    metric_group = "vm"
    metric_name = "vsanDomObj.readMaxLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVsanDomObjReadThroughputAverage(BaseVSphereMetricPuller):
    """Read throughput in kBps"""
    metric_group = "vm"
    metric_name = "vsanDomObj.readThroughput.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmVsanDomObjRecoveryWriteAvgLatencyAverage(
        BaseVSphereMetricPuller):
    """Average recovery write latency in ms"""
    metric_group = "vm"
    metric_name = "vsanDomObj.recoveryWriteAvgLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVsanDomObjRecoveryWriteCongestionAverage(
        BaseVSphereMetricPuller):
    """Recovery write congestion"""
    metric_group = "vm"
    metric_name = "vsanDomObj.recoveryWriteCongestion.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjRecoveryWriteIopsAverage(BaseVSphereMetricPuller):
    """Recovery write IOPS"""
    metric_group = "vm"
    metric_name = "vsanDomObj.recoveryWriteIops.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjRecoveryWriteMaxLatencyLatest(
        BaseVSphereMetricPuller):
    """Max recovery write latency in ms"""
    metric_group = "vm"
    metric_name = "vsanDomObj.recoveryWriteMaxLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVsanDomObjRecoveryWriteThroughputAverage(
        BaseVSphereMetricPuller):
    """Recovery write through-put in kBps"""
    metric_group = "vm"
    metric_name = "vsanDomObj.recoveryWriteThroughput.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10


class VSphereVmVsanDomObjWriteAvgLatencyAverage(BaseVSphereMetricPuller):
    """Average write latency in ms"""
    metric_group = "vm"
    metric_name = "vsanDomObj.writeAvgLatency.average"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVsanDomObjWriteCongestionAverage(BaseVSphereMetricPuller):
    """Write congestion"""
    metric_group = "vm"
    metric_name = "vsanDomObj.writeCongestion.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjWriteIopsAverage(BaseVSphereMetricPuller):
    """Write IOPS"""
    metric_group = "vm"
    metric_name = "vsanDomObj.writeIops.average"
    metric_type = "gauge"
    metric_unit = "num"
    pulling_interval = 10


class VSphereVmVsanDomObjWriteMaxLatencyLatest(BaseVSphereMetricPuller):
    """Max write latency in ms"""
    metric_group = "vm"
    metric_name = "vsanDomObj.writeMaxLatency.latest"
    metric_type = "cumulative"
    metric_unit = "ms"
    pulling_interval = 10


class VSphereVmVsanDomObjWriteThroughputAverage(BaseVSphereMetricPuller):
    """Write throughput in kBps"""
    metric_group = "vm"
    metric_name = "vsanDomObj.writeThroughput.average"
    metric_type = "gauge"
    metric_unit = "KBps"
    pulling_interval = 10
