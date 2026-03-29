# FuncDSL Task API Reference

Complete API reference for quarkus-flow FuncDSL task patterns.

## Calling Java Methods

~~~java
// Simple function call (input type inferred)
function(myService::process)

// Explicit input type
function(myService::process, ProcessRequest.class)

// Named (required when branching to this task)
function("processStep", myService::process, ProcessRequest.class)

// With workflow context (payload + context)
withContext((payload, ctx) -> svc.run(ctx, payload), Input.class)

// Agent call — uses unique id as memory id (for LangChain4j AI services)
agent("draftAgent", drafterAgent::draft, String.class)

// Agent with instance id (stateful agents, HITL loops)
withInstanceId((id, prompt) -> agent.run(id, prompt), Prompt.class)
~~~

## Data Flow: inputFrom / outputAs / exportAs

~~~java
// Extract a slice of the context as input
function(pricing::quote, QuoteRequest.class)
    .inputFrom("$.cart.quoteRequest")

// Transform the task result before merging
function(nlp::classify, Text.class)
    .outputAs("{ sentiment: ., reviewed: false }")

// Merge result back into global context
agent("draftNewsletter", drafter::draft, Draft.class)
    .exportAs((draft, wfCtx) -> {
        var current = (NewsletterContext) wfCtx.currentData();
        return current.withDraft(draft);
    }, Draft.class)
~~~

**Rule**: keep transformations close to the step that needs them. Don't
use global context mutations when a targeted `exportAs` will do.

## Branching

~~~java
// Single condition
switchWhen(".score >= 80", "sendStep")

// Typed predicate + else
switchWhenOrElse(
    (HumanReview h) -> h.needsRevision(),
    "reviseStep",
    "sendStep",
    HumanReview.class
)

// Typed predicate + directive (END, CONTINUE, etc.)
switchWhenOrElse(
    (HumanReview h) -> h.approved(),
    "sendStep",
    FlowDirectiveEnum.END,
    HumanReview.class
)
~~~

## Events (emit / listen)

~~~java
// Emit a JSON CloudEvent
emitJson("org.acme.newsletter.review.required", Review.class)

// Wait for a single event (HITL pattern)
listen("waitHuman", toOne("org.acme.review.done"))
    .outputAs((Collection<Object> c) -> c.iterator().next())

// Wait for any of several events
listen(toAny("org.acme.approved", "org.acme.rejected"))
~~~

## HTTP and OpenAPI Tasks

~~~java
// Fluent HTTP GET
get("https://service/api/resource")

// Named GET (required if you branch to it)
get("fetchUser", "https://service/users/" + id)

// POST with body
post(Map.of("name", "Ricardo"), "https://service/users")

// OpenAPI call
call(openapi()
    .document("https://petstore3.swagger.io/api/v3/openapi.json")
    .operation("findPetById"))
~~~

## Side Effects and Iteration

~~~java
// Fire-and-forget (no result merged to context)
consume("sendEmail",
    (HumanReview r) -> mailService.send("to@acme.com", "Subject", r.draft()),
    HumanReview.class
)

// Iterate over a collection
forEach(order -> order.items(),
    inner -> inner.tasks(
        function(inventoryService::reserve, Item.class)
    )
)
~~~
