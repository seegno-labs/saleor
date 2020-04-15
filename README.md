## Slyk Saleor

In order to adapt Saleor to our environment, we've had to make some significant changes, mainly due to our need for a multitenant and a multicurrency solution.

The logic to handle requests to our services in defined on:

* [domain_utils](https://github.com/seegno-labs/saleor/blob/develop/saleor/domain_utils.py)
  * This file has functions that will interact with some Slyk services and handle overall tenancy functionality to be done through HTTP or through Celery task manager.
* [domain_task](https://github.com/seegno-labs/saleor/blob/develop/saleor/domain_task.py)
  * This task is supposed to be used on any Celery task as a base to be inherited with. It will persist the domain that the Celery task will have to use, since every task will be executed in a freshly generated environment.
* [router](https://github.com/seegno-labs/saleor/blob/develop/saleor/core/db/router.py)
  * This is the database router to make sure the models from the database use the correct tenant connection. This is attached to django on the settings.py
* [schema](https://github.com/seegno-labs/saleor/blob/develop/saleor/core/db/schema.py)
  * This is a simple function to attach our search_path on every connection to the database to enable the database to use the proper schema.
* [migrate/tasks](https://github.com/seegno-labs/saleor/blob/develop/saleor/migrate/tasks.py)
  * Task that will delegate the django migration to a celery task so it can be done asynchronously.
* [migrate/views](https://github.com/seegno-labs/saleor/blob/develop/saleor/migrate/views.py)
  * The migrate endpoint implementation.


### File changes for multitenancy

- [saleor/urls.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/urls.py)
- [saleor/settings.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/settings.py)
- [saleor/checkout/utils.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/checkout/utils.py)
- [saleor/extensions/plugins/webhook/tasks.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/extensions/plugins/webhook/tasks.py)
- [saleor/graphql/account/mutations/base.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/account/mutations/base.py)
- [saleor/graphql/checkout/mutations.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/checkout/mutations.py)
- [saleor/graphql/core/utils/reordering.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/core/utils/reordering.py)
- [saleor/graphql/product/bulk_mutations/products.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/product/bulk_mutations/products.py)
- [saleor/graphql/product/mutations/attributes.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/product/mutations/attributes.py)
- [saleor/graphql/product/mutations/products.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/product/mutations/products.py)
- [saleor/menu/utils.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/menu/utils.py)
- [saleor/order/actions.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/order/actions.py)
- [saleor/order/utils.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/order/utils.py)
- [saleor/payment/utils.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/payment/utils.py)
- [saleor/product/tasks.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/product/tasks.py)
- [saleor/product/thumbnails.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/product/thumbnails.py)
- [saleor/product/utils/__init__.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/product/utils/__init__.py)
- [saleor/site/migrations/0013_assign_default_menus.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/site/migrations/0013_assign_default_menus.py) (The line changed here is `Site.objects.clear_cache` due to a persistence of the connection upon each migration)
- [saleor/warehouse/management.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/warehouse/management.py)
- [saleor/wishlist/models.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/wishlist/models.py)

### File changes due to dynamic currency

- [saleor/core/middleware.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/core/middleware.py)
- [saleor/core/taxes.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/core/taxes.py)
- [saleor/core/utils/__init__.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/core/utils/__init__.py)
- [saleor/discount/models.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/discount/models.py)
- [saleor/graphql/checkout/mutations.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/checkout/mutations.py)
- [saleor/graphql/order/mutations/draft_orders.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/order/mutations/draft_orders.py)
- [saleor/graphql/payment/mutations.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/payment/mutations.py)
- [saleor/graphql/product/mutations/products.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/product/mutations/products.py)
- [saleor/graphql/shop/types.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/graphql/shop/types.py)
- [saleor/order/utils.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/order/utils.py)
- [saleor/payment/models.py](https://github.com/seegno-labs/saleor/blob/develop/saleor/payment/models.py)

------------------------------------

![Saleor Commerce - A GraphQL-first platform for perfectionists](https://user-images.githubusercontent.com/249912/71523206-4e45f800-28c8-11ea-84ba-345a9bfc998a.png)

<div align="center">
  <h1>Saleor Commerce</h1>
</div>

<div align="center">
  <strong>Customer-centric e-commerce on a modern stack</strong>
</div>

<div align="center">
  A headless, GraphQL-first e-commerce platform delivering ultra-fast, dynamic, personalized shopping experiences. Beautiful online stores, anywhere, on any device.
</div>

<br>

<div align="center">
  Join our active, engaged community: <br>
  <a href="https://saleor.io/">Website</a>
  <span> | </span>
  <a href="https://medium.com/saleor">Blog</a>
  <span> | </span>
  <a href="https://twitter.com/getsaleor">Twitter</a>
  <span> | </span>
  <a href="https://gitter.im/mirumee/saleor">Gitter</a>
  <span> | </span>
  <a href="https://spectrum.chat/saleor">Spectrum</a>
</div>

<br>

<div align="center">
  <a href="https://circleci.com/gh/mirumee/saleor">
    <img src="https://circleci.com/gh/mirumee/saleor.svg?style=svg" alt="Build status" />
  </a>
  <a href="http://codecov.io/github/mirumee/saleor?branch=master">
    <img src="http://codecov.io/github/mirumee/saleor/coverage.svg?branch=master" alt="Codecov" />
  </a>
  <a href="https://docs.saleor.io/">
    <img src="https://img.shields.io/badge/docs-docs.saleor.io-brightgreen.svg" alt="Documentation" />
  </a>
  <a href="https://github.com/python/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  </a>
</div>

## Table of Contents

- [What makes Saleor special?](#what-makes-saleor-special)
- [Features](#features)
- [Installation](#installation)
- [Documentation](#documentation)
- [Demo](#demo)
- [Contributing](#contributing)
- [Translations](#translations)
- [Your feedback](#your-feedback)
- [License](#license)

## What makes Saleor special?

Saleor is a rapidly-growing open source e-commerce platform that has served high-volume companies from branches like publishing and apparel since 2012. Based on Python and Django, the latest major update introduces a modular front end powered by a GraphQL API and written with React and TypeScript.

## Features

- **PWA**: End users can shop offline for better sales and shopping experiences
- **GraphQL API**: Access all data from any web or mobile client using the latest technology
- **Headless commerce**: Build mobile apps, customize storefronts and externalize processes
- **UX and UI**: Designed for a user experience that rivals even the top commercial platforms
- **Dashboard**: Administrators have total control of users, processes, and products
- **Orders**: A comprehensive system for orders, dispatch, and refunds
- **Cart**: Advanced payment and tax options, with full control over discounts and promotions
- **Payments**: Flexible API architecture allows integration of any payment method. It comes with Braintree support out of the box.
- **Geo-adaptive**: Automatic localized pricing. Over 20 local languages. Localized checkout experience by country.
- **SEO**: Packed with features that get stores to a wider audience
- **Cloud**: Optimized for deployments using Docker
- **Analytics**: Server-side Google Analytics to report e-commerce metrics without affecting privacy

Saleor is free and always will be.
Help us out… If you love free stuff and great software, give us a star! 🌟

![Saleor Storefront - React-based PWA e-commerce storefront](https://user-images.githubusercontent.com/249912/71527146-5b6be280-28da-11ea-901d-eb76161a6bfb.png)
![Saleor Dashboard - Modern UI for managing your e-commerce](https://user-images.githubusercontent.com/249912/71523261-8a795880-28c8-11ea-98c0-6281ea37f412.png)

## Installation

Saleor requires Python 3.8, Node.js 10.0+, PostgreSQL and OS-specific dependency tools.

[See the Saleor docs](https://docs.saleor.io/docs/getting-started/intro/) for step-by-step installation and deployment instructions.

## Documentation

Saleor documentation is available here: [docs.saleor.io](https://docs.saleor.io)

To contribute, please see the [`mirumee/saleor-docs` repository](https://github.com/mirumee/saleor-docs/).

## Storefront

For PWA, single-page torefront go to the [saleor-storefront](https://github.com/mirumee/saleor-storefront) repository.

[View storefront demo](https://pwa.saleor.io/)

## Dashboard

For dashboard go to the [saleor-dashboard](https://github.com/mirumee/saleor-dashboard) repository.

[View dashboard demo](https://pwa.saleor.io/dashboard/)

## Demo

Want to see Saleor in action?

[View Storefront](https://pwa.saleor.io/) | [View Dashboard (admin area)](https://pwa.saleor.io/dashboard/)

Or launch the demo on a free Heroku instance.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Login credentials: `admin@example.com`/`admin`

## Contributing

We love your contributions and do our best to provide you with mentorship and support. If you are looking for an issue to tackle, take a look at issues labeled [`Help Wanted`](https://github.com/mirumee/saleor/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22).

If nothing grabs your attention, check [our roadmap](https://github.com/mirumee/saleor/projects/6) or come up with your feature. Just drop us a line or [open an issue](https://github.com/mirumee/saleor/issues/new) and we’ll work out how to handle it.

Get more details in our [Contributing Guide](https://docs.getsaleor.com/docs/contributing/intro/).

## Legacy views

If you're interested in using the old version of Saleor, go the [legacy-views](https://github.com/mirumee/legacy-views) repository. It contains the 2.9.0 release, which includes Django-based views and HTML templates of Storefront 1.0 and Dashboard 1.0. Note: this version of Saleor is no longer officially maintained.


## Your feedback

Do you use Saleor as an e-commerce platform?
Fill out this short survey and help us grow. It will take just a minute, but mean a lot!

[Take a survey](https://mirumee.typeform.com/to/sOIJbJ)

## License

Disclaimer: Everything you see here is open and free to use as long as you comply with the [license](https://github.com/mirumee/saleor/blob/master/LICENSE). There are no hidden charges. We promise to do our best to fix bugs and improve the code.

Some situations do call for extra code; we can cover exotic use cases or build you a custom e-commerce appliance.

#### Crafted with ❤️ by [Mirumee Software](http://mirumee.com)

hello@mirumee.com
