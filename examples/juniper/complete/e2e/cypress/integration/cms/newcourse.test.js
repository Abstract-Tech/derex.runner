const coursename = "test " + Math.floor(Math.random() * 100000);
const courserun =
  new Date().getFullYear() + "_" + Math.floor(Math.random() * 10);
const youtubeURL = "https://www.youtube.com/watch?v=GF60Iuh643I";

function makeChar(length) {
  let result = "";
  let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  let charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

const coursenum = makeChar(2) + Math.floor(Math.random() * 1000);
let count = 0;

const $click = ($el) => {
  count += 1;
  return $el.click();
};

describe("create new course test", () => {
  const cms_url = Cypress.env("CMS_URL");

  it("allows admin user access", async () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));

    cy.get(".new-course-button")
      .wait(1000)
      .then(($button) => {
        cy.wrap($button).click();
      });

    cy.get("#new-course-name").type(coursename);
    cy.get("#new-course-org").type("Abstract");
    cy.get("#new-course-number").type(coursenum);
    cy.get("#new-course-run").type(courserun);
    cy.get(".new-course-save").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".add-section .button").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".add-subsection .button").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".add-unit .button").then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".new-component-type .add-xblock-component-button[data-type='discussion']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".edit-button").click();
    cy.get("#xb-field-edit-display_name").clear().type("blabla");
    cy.get("#xb-field-edit-discussion_category").clear().type("week 3");
    cy.get("#xb-field-edit-discussion_target").clear().type("level 1");
    cy.get(".save-button").click();
    cy.get(
      ".new-component-type .add-xblock-component-button[data-type='video']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".new-component-type .add-xblock-component-button[data-type='problem']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".new-component-template .button-component[data-boilerplate='multiplechoice.yaml']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".new-component-type .add-xblock-component-button[data-type='problem']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".new-component-template .button-component[data-boilerplate='multiplechoice_hint.yaml']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".new-component-type .add-xblock-component-button[data-type='html']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(
      ".editor-md .button-component[data-boilerplate='announcement.yaml']"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    cy.get(".action-publish").then(($button) => {
      cy.wrap($button).click();
    });
  });
});
