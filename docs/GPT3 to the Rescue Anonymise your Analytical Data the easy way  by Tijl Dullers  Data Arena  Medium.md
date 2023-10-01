[

![Tijl Dullers](https://miro.medium.com/v2/resize:fill:88:88/1*MiTuDIZaW9c4he004YCnfw.jpeg)



](https://medium.com/@tijldullers?source=post_page-----6f836616ba6f--------------------------------)[

![Data Arena](https://miro.medium.com/v2/resize:fill:48:48/1*7mtMygQZeWLAIrdDXuFjsA.png)



](https://medium.com/data-arena?source=post_page-----6f836616ba6f--------------------------------)

![](https://miro.medium.com/v2/resize:fit:700/0*v3oqTvyq9OEgiSrz.png)

Image Created using [MidJourney](https://www.midjourney.com/) v4 by Author

Did you ever try to anonymise large volumes of data in a complex data landscape?

-   Finding direct and indirect personal data across all tables in your entire data estate?
-   Defining the anonymisation action and method that is best fit for a particular data element?

**If you have, you know it’s a tedious and time consuming task!**

Luckily, there is a myriad of tools available to make your life significantly easier.

-   Some are based on scanning column names, while others also look at the content of your data.
-   The more advanced ones are based on a technique called Named Entity Resolution (NER). While the more basic ones use regular expressions to detect patterns such as National Identity Numbers, IBAN account numbers and the like.

**Just some examples:**

With all this nice tech available to make a tedious task somewhat less time consuming and boring.

You might ask: “What tools do professional consultants generally use?” The answer might surprise you: “They most often use Microsoft Excel” ;-)

Of course, none of the available tools are perfect.

Most of them are primarily trained on- or configured for U.S. data sets and they always require some tweaking and human verification. But if the task at hand is big enough, diving into them is certainly worth the effort.

## GPT-3 to the Rescue

> So, “GPT-3 to the rescue!”, you said?

After some recent fiddling with GPT-3 DaVinci 2 on the OpenAI Playground ([https://beta.openai.com/playground](https://beta.openai.com/playground)), I thought it would be a cool idea to have a look and see how good it is at identifying Personal data and suggesting a preferred anonymisation technique. Does magic really exist within a single prompt? Let’s find out!

Based on the best advice I could find online, a good prompt is specific in terms of the to be achieved result, and should include some concrete examples.

**So let’s try the following, shall we:**

-   We instruct GPT-3 to indicate for each attribute if it is direct or indirect personal information.
-   We ask it to propose an anonymisation action and method.
-   We include some examples as part of the prompt.

```
Indicate for each attribute (=>) if it contains direct or indirect personal information and its sensitivity according to the GDPR regulation, include if the attribute should be anonymized and recommend the best method (keep, supress, aggregate,randomize, generalise )to ensure personal information is anonymized while keeping maximal insight for statistical processing purposes.Examples:    "field": {      "attribute-name": "customer id",      "attribute-value": "1345654",      "attribute-entity": "identifier",      "information-type": "direct personal information",      "sensitivity": "low",      "anonymization": "keep",      "anonymization-method": "keep"    }    "field": {      "attribute-name": "first name",      "attribute-value": "John",      "attribute-entity": "natural person name",      "information-type": "direct personal information",      "sensitivity": "low",      "anonymization": "suppress",      "anonymization-method": "blank out"    }    "field": {      "attribute-name": "address",      "attribute-value": "Stoepstraat 64",      "attribute-entity": "physical person address",      "information-type": "direct personal information",      "sensitivity": "low",      "anonymization": "generalise",      "anonymization-method": "street only"    }    "field": {      "attribute-name": "zipcode",      "attribute-value": "3150",      "attribute-entity": "postal code",      "information-type": "indirect personal information",      "sensitivity": "low",      "anonymization": "keep",      "anonymization-method": "keep"    "field": {      "attribute-name": "P-gen",      "attribute-value": "Male",      "attribute-entity": "gender",      "information-type": "indirect personal information",      "sensitivity": "medium",      "anonymization": "supress",      "anonymization-method": "supress"    }    "field": {      "attribute-name": "birth date",      "attribute-value": "13/08/1982",      "information-type": "birthdate",      "sensitivity": "medium",      "anonymization": "generalise",      "anonymization-method": "month and year only"    }    "field": {      "attribute-name": "smoking habit",      "attribute-value": "Heavy Smoker",      "attribute-entity": "biometric data",      "information-type": "indirect personal information",      "sensitivity": "high",      "anonymization": "keep",      "anonymization-method": "keep"    }    "field": {      "attribute-name": "products",      "attribute-value": [        "Product1",        "Product2"      ],      "information-type": "non-personal information",      "attribute-entity": "product information",      "sensitivity": "low",      "anonymization": "keep",      "anonymization-method": "keep"    }    "field": {      "attribute-name": "national identity number",      "attribute-value": "79082215542",      "attribute-entity": "personal identifier",      "information-type": "direct personal information",      "sensitivity": "high",      "anonymization": "randomize",      "anonymization-method": "regenerate"    }Prompt:"field": {     "attribute-name": "B-Day",     "attribute-value": "21/02/1943",     "attribute-entity": "=>",      "information-type": "=>",      "sensitivity": "=>",      "anonymization": "=>",      "anonymization-method": "=>"    }
```

After making some test runs and feeding it different kinds of attributes, with obscure column names and different types of values, I must say I’m impressed!

-   In a lot of cases GPT-3 successfully identifies the supplied personal data entity
-   Also, it provides a rather consistent proposed anonymisation action and method
-   Even if you change the attribute-name (the name of the database column) to something a bit obscure, it still does a great job!

![](https://miro.medium.com/v2/resize:fit:700/1*f5li5YAiM-u41UrfKLrLTQ.png)

Some Input => Output Examples fed to GPT-3 based on the Prompt defined above — Image by Author

## **Conclusions?**

So, I don’t know if you’re as dazzled as I was when seeing these kinds of results. Yes, you might find a lot of edge cases, and the proposed anonymisation actions are debatable. But nothing some tweaking cannot fix!

> And foremost, when you ask GPT-3 to apply the rules as set out by the GDPR regulation, it even seems to know what you are talking about! That’s more than what you can say of about 90 percent of the human population.

**Some Caveats and potential solutions**

Of course, there are some caveats to this way of working:

1.  **Cost:** While GPT-3 is not very expensive, running millions of attributes through it’s API’s might get costly. But there’s an easy solution for this. You’re totally not obliged to scan each row of each table attribute, but can do some sampling (e.g. using a random select) and evaluate for instance only 100 rows per attribute. Another element that drives the cost is the length of the used prompt. Without any doubt our prompt does not need that many examples and can be formulated more concisely.

**2\. Privacy:** One of my first thoughts while reading this would be:

> “Hey but, you are sending personal information to an API in the Cloud, what a nice way to improve the GDPR compliance of your Data Landscape” ;-)

Well, that would be a fair remark:

-   If you’re a company located in Europe, just by sending pieces of personal information to the API’s of OpenAI’s GPT-3 you might run into some [Schrems II](https://noyb.eu/en/privacy-shield-20-first-reaction-max-schrems) related issues. So, until there is a reliable framework on Trans-Atlantic Data Transfers, that certainly is something to think about.
-   And what is OpenAI actually doing with the data you send them? The Privacy Policy on their website states that they can use the data you send them for the (re)training of their models, but state that they remove all personal data before doing so! And you can even make a specific request not to use your data for training purposes.

> Let that sink in for a while, … OpenAI automatically removes all personal information from the data they collect before using it for training purposes, well that might explain why they are so good at detecting PI in the first place, isn’t it?

-   And there’s more good news, as recently announced by Microsoft they established an exclusive agreement with OpenAI to integrate its services into the Azure ecosystem, and would add things like security and compliance on top. I can’t find if they will offer a GPT3 API service that is fully localised in Europe, but who knows.

**3\. No “Offline Mode”:** For companies in regulated industries, exchanging personal data with a Public Cloud service might be an issue. But that brings us to another interesting use-case of this GPT-3 capability. It can also be used to train offline language models like [BERT](https://www.techtarget.com/searchenterpriseai/definition/BERT-language-model) to better cope with this type of use cases.

**4\. Accountability:** Last but not least, one of the caveats of using an NLP model — to identify personal information and let it propose how to anonymise it — is the question on who is accountable, when the model made an incorrect judgement.

The answer is clear, **it’s you!** But this is always the case, no matter if you use raw human brain power, an offline tool or a more advanced engine like GPT-3.

To close off, another interesting use of the above mentioned scenario is to add all generated metadata into your Data Catalogue!

If you Data Catalog supports the [Atlas REST API’s](https://atlas.apache.org/api/v2/index.html) it should not be too difficult to achieve this in under 20 lines of code.

**In case you have any questions or like to further discuss about this topic.**

**Don’t hesistate to reach out:** [**https://www.linkedin.com/in/tijldullers/**](https://www.linkedin.com/in/tijldullers/)