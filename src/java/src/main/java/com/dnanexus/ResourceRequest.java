// Copyright (C) 2014 DNAnexus, Inc.
//
// This file is part of dx-toolkit (DNAnexus platform client libraries).
//
//   Licensed under the Apache License, Version 2.0 (the "License"); you may
//   not use this file except in compliance with the License. You may obtain a
//   copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
//   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
//   License for the specific language governing permissions and limitations
//   under the License.

package com.dnanexus;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.base.Preconditions;

/**
 * A request for resources for a single job.
 */
@JsonInclude(Include.NON_NULL)
public class ResourceRequest {
    /**
     * Returns a ResourceRequest that specifies the requested instance type.
     *
     * @param instanceType DNAnexus instance type, e.g. "dx_m1.large"
     *
     * @return a ResourceRequest object
     */
    public static ResourceRequest withInstance(String instanceType) {
        return new ResourceRequest(instanceType);
    }

    @JsonProperty
    public final String instanceType;

    /**
     * Initializes a ResourceRequest with the specified instance type.
     *
     * @param instanceType DNAnexus instance type, e.g. "dx_m1.large"
     */
    private ResourceRequest(String instanceType) {
        Preconditions.checkNotNull(instanceType, "instanceType may not be null");
        this.instanceType = instanceType;
    }

    /**
     * Returns the instance type string that was specified.
     *
     * @return instance type
     */
    public String getInstanceTypeString() {
        return instanceType;
    }
}
