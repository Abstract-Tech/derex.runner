/* const fs = require("fs");
 */
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
const cms_url = Cypress.env("CMS_URL");
describe("create new course test", () => {
  it("allows admin to import a course", async () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.get(".new-course-button").wait(1000).click();
    cy.get("#new-course-name").type(coursename);
    cy.get("#new-course-org").type("Abstract");
    cy.get("#new-course-number").type(coursenum);
    cy.get("#new-course-run").type(courserun);
    cy.get(".new-course-save").wait(2000).click();
    cy.visit(`${cms_url}/course/course-v1:course+lm101+2012_5`);
    cy.get(".nav-course-tools > .title").wait(1000).click();
    cy.get(".nav-course-tools-import > a").wait(1000).click();
    cy.importCourse("courses/course.tar.gz");
    cy.get("#replace-courselike-button").wait(1000).click();
    cy.get("#view-updated-button").wait(10000).click();
  });
});
