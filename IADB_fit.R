#This script takes the data queried and processed on Python to fit the models

#Setup and prep
inst_check <- function(pack,ver=NULL) {
  if (pack %in% installed.packages()[,1]) {
    if (ver == installed.packages()[pack,"Version"]) {
      print(paste("Package",pack,"is installed with the target version",ver))
    } else {
      if (!require("remotes")) {
        install.packages("remotes")
        require(remotes)
        remotes::install_version(pack, version = ver, upgrade = "never")
      } else {
        require(remotes)
        remotes::install_version(pack, version = ver, upgrade = "never")
      }
    }
  } else {
    if (!require("remotes")) {
      install.packages("remotes")
      require(remotes)
      remotes::install_version(pack, version = ver, upgrade = "never")
    } else {
      require(remotes)
      remotes::install_version(pack, version = ver, upgrade = "never")
    }    
  }
}

inst_check(pack = "betareg", ver = "3.2-4")
inst_check(pack = "StepBeta", ver = "2.1.0")
inst_check(pack = "lmtest", ver = "0.9-40")
inst_check(pack = "ggplot2", ver = "3.5.1")
inst_check(pack = "gglm", ver = "1.0.4")
inst_check(pack = "broom", ver = "1.0.7")

library(broom)
library(gglm)
library(betareg)
library(StepBeta)
library(lmtest)
library(ggplot2)

data <- read.csv("data_final.csv")
data$year <- as.factor(data$year)
data$country <- as.factor(data$country)
data <- na.omit(data) #Need to drop NAs to be able to use the Likelihood Ratio Test later in the code.

#Linear regression models
mod1 <- lm(ninis_2_15_24~.,data = data)

print(summary(mod1))
gglm(mod1)
summary_mod1<-tidy(mod1)
write.csv(summary_mod1,"summary_full_linear.csv")

modnulllm <- lm(ninis_2_15_24~country+year,data = data)

step <- step(modnulllm,scope = list(lower=modnulllm,upper=mod1),direction = "both")
print(summary(step))
gglm(step)
summary_step<-tidy(step)
write.csv(summary_step,"summary_step_linear.csv")

#Beta regression models
mod2 <- betareg(ninis_2_15_24 ~ . | year, data = data)
print(summary(mod2))
plot(mod2,which=c(1,2,4,6),type="pearson")
#
#
#
#
summary_mod2<-tidy(mod2)
write.csv(summary_mod2,"summary_full_beta.csv")

step2 <- StepBeta(mod2,k=2)
print(summary(step2))
plot(step2,which=c(1,2,4,6),type="pearson")
#
#
#
#
summary_step2<-tidy(step2)
write.csv(summary_step2,"summary_step_beta.csv")

mod2b <- betareg(ninis_2_15_24 ~ country + year + tasa_desocupacion + tasa_participacion + 
                horas_trabajadas + salinfor_total + jefa_ch + salmin_total + inflation_minus_1 | year,
                data = data)
print(summary(mod2b))
plot(mod2b,which=c(1,2,4,6),type="pearson")
#
#
#
#
summary_mod2b<-tidy(mod2b)
write.csv(summary_mod2b,"summary_final_beta.csv")

print(lrtest(mod2,mod2b))
print(lrtest(mod2,step2))
print(lrtest(step2,mod2b))