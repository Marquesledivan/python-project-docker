node('ti') {
    try {
        def PROJECT = "ledivan-hoteis"
        def REPO_GIT = "git@git.ledivan.com.br:ledivan-hoteis.git"
        def BRANCH_NAME = "master"
        def IMAGE_VERSION = "$BUILD_NUMBER"

        def ECR_URL = "ledivan.dkr.ecr.sa-east-1.amazonaws.com/ledivanhotel"

        def CRONJOB_NAME = "$PROJECT-cronjob"
        def CRONJOB_FILE = "$PROJECT-cronjob.yaml"


        def K8S_NAMESPACE = "$PROJECT"
        def KUBECTL = "kubectl --kubeconfig /kube/.kube/config"



        message = "PIPELINE STARTED IN BRANCH $BRANCH_NAME - Build $BUILD_NUMBER"
        notifyBuild(message)

        stage("cloning_$PROJECT") {
                checkout([$class: 'GitSCM',
                    userRemoteConfigs: [[url: "$REPO_GIT"]],
                    branches: [[name: "$BRANCH_NAME"]],
                    credentialsId: 'f2504523-0111-41a4-a9be-f7d2b40163af',
                    clean: false,
                    extensions: [[$class: 'SubmoduleOption',
                                    disableSubmodules: false,
                                    parentCredentials: false,
                                    recursiveSubmodules: true,
                                    reference: '',
                                    trackingSubmodules: false]],
                    doGenerateSubmoduleConfigurations: false,
                    submoduleCfg: []
                ])
        }

        stage('push_container_to_ECR') {
            def LOGIN_CMD = sh(script: "aws ecr get-login --profile ti --no-include-email --region sa-east-1", returnStdout: true)
            dir(env.WORKSPACE) {
                sh """
                    ${LOGIN_CMD}
                    docker build -t $ECR_URL:$IMAGE_VERSION -f Dockerfile .
                    docker push $ECR_URL:$IMAGE_VERSION
                """
            }
        }

        stage('change_image_name') {
            dir(env.WORKSPACE) {
                sh """
                    egrep -lRZ '__TAG__' . | xargs -0 -l sed -i -e 's/__TAG__/'$IMAGE_VERSION'/g'
                """
            }
        }

        stage('k8s_create_structures') {
            dir(env.WORKSPACE) {
                sh """
                    cd kubernetes
                    $KUBECTL apply -f namespace.yaml
              """
            }
        }

        stage('k8s_create_cronjobs') {
            dir(env.WORKSPACE) {
                sh """
                    cd kubernetes
                    sed -i s/__TAG__/$IMAGE_VERSION/ $CRONJOB_FILE
                    $KUBECTL apply -f $CRONJOB_FILE
                """
            }
        }

    } catch (error) {
        currentBuild.result = "FAILED"
        throw error
    } finally {
        notifyBuild("", currentBuild.result)
    }
}

def notifyBuild(String message, String buildStatus = 'STARTED') {
    def SLACK_URL = "https://hooks.slack.com/services/ledivan/ledivan/"
    def SLACK_TOKEN = "ledivan"
    def SLACK_CHANNEL = "#ledivan-hoteis"

    buildStatus = buildStatus ?: 'SUCCESSFUL'
    def subject = "${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    def summary = "${subject} (${env.JOB_URL})"

    if (buildStatus == 'STARTED') {
        colorCode = '#FFFF00' // Yellow
    } else if (buildStatus == 'SUCCESSFUL' || buildStatus == 'SUCCESS') {
        colorCode = '#00FF00' // Green
    } else if (buildStatus == 'INFO') {
        colorCode = '#0080FF' // Blue
    } else {
        colorCode = '#FF0000' // Red
    }

    slackSend (color:"${colorCode}",
        baseUrl: SLACK_URL,
        token: SLACK_TOKEN,
        channel: SLACK_CHANNEL,
        message: "${summary} ${message}")
}