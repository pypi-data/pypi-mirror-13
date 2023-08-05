# OpenTracing API for Python

This library is a Python implementation of Open Tracing API.

## Objectives

Distributed tracing and context propagation have become important analysis 
tools for today's multi-layer distributed systems comprised of numerous 
micro-services implemented in different languages.  The success of these
tools is dependent on pervasive instrumentation of applications and 
libraries with trace context propagation support.

The OpenTracing project (http://opentracing.github.io) provides a multi-lingual 
standard for application-level instrumentation that's loosely coupled to any 
particular downstream tracing or monitoring system. In this way, adding or 
switching tracing implementations becomes an O(1) code change.

## Status

In the current version, `opentracing-python` provides only the API and a 
basic no-op implementation that can be used by instrumentation libraries to 
collect and propagate distributed tracing context.

Future versions will include a reference implementation utilizing an 
abstract Recorder interface, as well as a (Zipkin)
[http://openzipkin.github.io]-compatible Tracer.

## Concepts

**Trace** is a virtual representation of the path a request takes through 
the layers and services of a (potentially distributed) system.

**Span** is a representation of any logical unit of work in the system. 
Spans can be nested and ordered to model parent-child and casual 
relationships. A Trace is tree of Spans. 

**Trace Context** encapsulates the smallest amount of state needed to 
describe a Span's identity within a larger, potentially distributed trace,
sufficient to propagate the context of a particular trace between processes.

**Trace Attributes** is a collection of key/value pairs stored in a Trace 
Context and propagated to all future children Spans. Given a full-stack 
OpenTracing integration, Trace Attributes enable powerful functionality 
of transparently propagating  arbitrary application data, from a mobile app 
all the way into the depth of a storage system. It comes with powerful 
*costs* as well, since the attributes are propagated *in-band*, alongside 
with the application data; use this feature with care.

## Usage

The work of instrumentation libraries generally consists of three steps:

1. When a service receives a new request (over HTTP or some other protocol),
it uses OpenTracing API serialization tools to extract a Trace Context 
from the request headers and create a Span object. If the request does
not contain a trace context, the service starts a new trace and a new 
*root* Span.
2. The service needs to store the current Span in some request-local storage,
where it can be retrieved from when a child Span must be created, e.g. in 
case of the service making an RPC to another service.
3. When making outbound calls to another service, the current Span must be 
retrieved from request-local storage, a child span must be created using
`span.start_child()` method, and the Trace Context of the child span must
be serialized into the outbound request (e.g. HTTP headers) using 
OpenTracing API serialization tools.

Below are the code examples for steps 1 and 3. Implementation of 
request-local storage needed for step 2 is specific to the service and/or 
frameworks / instrumentation libraries it is using (TODO reference to other
OSS projects with examples of instrumentation).

### Inbound request

Somewhere in your server's request handler code:

```python

    def handle_request(request):
        span = before_request(request, opentracing.tracer)
        # use span as Context Manager to ensure span.finish() will be called
        with span:
            # store span in some request-local storage
            with RequestContext(span):
                # actual business logic
                handle_request_for_real(request)
        
    
    def before_request(request, tracer):
        context = tracer.trace_context_from_text(
            trace_context_id=request.headers, 
            trace_attributes=request.headers
        )
        operation = request.operation
        if context is None:
            span = tracer.start_trace(operation_name=operation)
        else:
            span = tracer.join_trace(operation_name=operation,
                                     parent_trace_context=context)
    
        span.add_tag('client.http.url', request.full_url)
    
        remote_ip = request.remote_ip
        if remote_ip:
            span.add_tag(tags.PEER_HOST_IPV4, remote_ip)
    
        caller_name = request.caller_name
        if caller_name:
            span.add_tag(tags.PEER_SERVICE, caller_name)
    
        remote_port = request.remote_port
        if remote_port:
            span.add_tag(tags.PEER_PORT, remote_port)
    
        return span
```

### Outbound request

Somewhere in your service that's about to make an outgoing call:

```python

    # create and serialize a child span and use it as context manager
    with before_http_request(
        request=out_request,
        current_span_extractor=RequestContext.get_current_span):
    
        # actual call
        return urllib2.urlopen(request)
    
    
    def before_http_request(request, current_span_extractor):
        op = request.operation
        parent_span = current_span_extractor()
        if parent_span is None:
            span = opentracing.tracer.start_trace(operation_name=op)
        else:
            span = parent_span.start_child(operation_name=op)
    
        span.add_tag('server.http.url', request.full_url)
        service_name = request.service_name
        host, port = request.host_port
        if service_name:
            span.add_tag(tags.PEER_SERVICE, service_name)
        if host:
            span.add_tag(tags.PEER_HOST_IPV4, host)
        if port:
            span.add_tag(tags.PEER_PORT, port)
    
        h_ctx, h_attr = opentracing.tracer.trace_context_to_text(
            trace_context=span.trace_context)
        for key, value in h_ctx.iteritems():
            request.add_header(key, value)
        if h_attr:
            for key, value in h_attr.iteritems():
                request.add_header(key, value)
    
        return span
```

# Development

## Tests

```
virtualenv env
source env/bin/activate
make bootstrap
make test
```

## Releases

```
pip install zest.releaser[recommended]
prerelease
release
python setup.py sdist upload -r pypi
postrelease
```

