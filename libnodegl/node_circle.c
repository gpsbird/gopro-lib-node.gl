/*
 * Copyright 2017 GoPro Inc.
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

#include <math.h>
#include <stddef.h>
#include <string.h>
#include "log.h"
#include "math_utils.h"
#include "nodegl.h"
#include "nodes.h"
#include "utils.h"

#define OFFSET(x) offsetof(struct geometry, x)
static const struct node_param circle_params[] = {
    {"radius",  PARAM_TYPE_DBL, OFFSET(radius),  {.dbl=1.0}},
    {"npoints", PARAM_TYPE_INT, OFFSET(npoints), {.i64=16}},
    {NULL}
};

static int circle_init(struct ngl_node *node)
{
    int ret = -1;
    struct geometry *s = node->priv_data;

    if (s->npoints < 3) {
        LOG(ERROR, "invalid number of points (%d < 3)", s->npoints);
        return -1;
    }

    float *vertices  = calloc(s->npoints, sizeof(*vertices)  * 3);
    float *texcoords = calloc(s->npoints, sizeof(*texcoords) * 2);
    float *normals   = calloc(s->npoints, sizeof(*normals)   * 3);

    if (!vertices || !texcoords || !normals)
        goto end;

    const float step = 2.f * M_PI / s->npoints;
    for (int i = 0; i < s->npoints; i++) {
        const float angle = i * step;
        const float x = sin(angle) * s->radius;
        const float y = cos(angle) * s->radius;
        vertices[i*3 + 0] = x;
        vertices[i*3 + 1] = y;
        texcoords[i*2 + 0] = (x + 1.f) / 2.f;
        texcoords[i*2 + 1] = (1.f - y) / 2.f;
    }

    static const float center[3] = {0};
    ngli_vec3_normalvec(normals, (float *)center, vertices, vertices + 3);
    for (int i = 1; i < s->npoints; i++)
        memcpy(normals + (i * 3), normals, 3 * sizeof(*normals));

    s->vertices_buffer = ngli_geometry_generate_buffer(node->ctx,
                                                       NGL_NODE_BUFFERVEC3,
                                                       s->npoints,
                                                       s->npoints * sizeof(*vertices) * 3,
                                                       vertices);

    s->texcoords_buffer = ngli_geometry_generate_buffer(node->ctx,
                                                        NGL_NODE_BUFFERVEC2,
                                                        s->npoints,
                                                        s->npoints * sizeof(*texcoords) * 2,
                                                        texcoords);

    s->normals_buffer = ngli_geometry_generate_buffer(node->ctx,
                                                      NGL_NODE_BUFFERVEC3,
                                                      s->npoints,
                                                      s->npoints * sizeof(*normals) * 3,
                                                      normals);

    s->indices_buffer = ngli_geometry_generate_indices_buffer(node->ctx, s->npoints);

    if (!s->vertices_buffer || !s->texcoords_buffer || !s->indices_buffer || !s->normals_buffer)
        goto end;

    s->draw_mode = GL_TRIANGLE_FAN;
    s->draw_type = GL_UNSIGNED_INT;

    ret = 0;

end:
    free(vertices);
    free(texcoords);
    free(normals);
    return ret;
}

#define NODE_UNREFP(node) do {                    \
    if (node) {                                   \
        ngli_node_detach_ctx(node);               \
        ngl_node_unrefp(&node);                   \
    }                                             \
} while (0)

static void circle_uninit(struct ngl_node *node)
{
    struct geometry *s = node->priv_data;

    NODE_UNREFP(s->vertices_buffer);
    NODE_UNREFP(s->texcoords_buffer);
    NODE_UNREFP(s->normals_buffer);
    NODE_UNREFP(s->indices_buffer);
}

const struct node_class ngli_circle_class = {
    .id        = NGL_NODE_CIRCLE,
    .name      = "Circle",
    .init      = circle_init,
    .uninit    = circle_uninit,
    .priv_size = sizeof(struct geometry),
    .params    = circle_params,
};