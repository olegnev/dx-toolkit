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

import java.util.Map;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;

/**
 * Specifies system requirements for a parent job (optionally overriding with different system
 * requirements for each entry point).
 */
public class SystemRequirements {
    /**
     * Deserializes system requirements from JSON.
     */
    @SuppressWarnings("unused")
    @JsonCreator
    private static SystemRequirements create(Map<String, ResourceRequest> systemRequirements) {
        return new SystemRequirements(systemRequirements);
    }

    /**
     * This is basically the JSON serialized hash. It may contain a key "*" representing the default
     * and keys for any other entry point overrides.
     *
     * This class is immutable, so do not allow direct access to this Map.
     */
    private Map<String, ResourceRequest> systemRequirements;

    /**
     * Initializes system requirements from the specified map.
     */
    private SystemRequirements(Map<String, ResourceRequest> systemRequirements) {
        this.systemRequirements =
                Preconditions
                        .checkNotNull(systemRequirements, "systemRequirements may not be null");
        for (Map.Entry<String, ResourceRequest> entry : this.systemRequirements.entrySet()) {
            Preconditions.checkNotNull(entry.getValue(),
                    "Resource request for key " + entry.getKey() + " may not be null");
        }
    }

    /**
     * Returns the default resource request (to be applied to entry points that are not explicitly
     * overridden).
     *
     * @return default resource request
     */
    public ResourceRequest getDefaultResourceRequest() {
        if (systemRequirements.containsKey("*")) {
            return systemRequirements.get("*");
        } else {
            return null;
        }
    }

    /**
     * Returns the resource request for the specified entry point.
     *
     * @param entryPointName name of entry point
     *
     * @return resource request
     */
    public ResourceRequest getResourceRequestForEntryPoint(String entryPointName) {
        // TODO: should entryPointName == "*" be disallowed here?
        if (systemRequirements.containsKey(entryPointName)) {
            return systemRequirements.get(entryPointName);
        } else {
            return null;
        }
    }

    /**
     * Serializes system requirements to JSON.
     */
    @SuppressWarnings("unused")
    @JsonValue
    private Map<String, ResourceRequest> getValue() {
        return ImmutableMap.copyOf(systemRequirements);
    }
}
