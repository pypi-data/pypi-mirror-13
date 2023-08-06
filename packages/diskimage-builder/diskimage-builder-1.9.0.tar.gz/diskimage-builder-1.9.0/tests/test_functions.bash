export TEST_ELEMENTS=$(dirname $0)/elements
export DIB_ELEMENTS=$(dirname $0)/../elements
export DIB_CMD=$(dirname $0)/../bin/disk-image-create

function build_test_image() {
    format=${1:-}

    if [ -n "$format" ]; then
        type_arg="-t $format"
    else
        type_arg=
        format="qcow2"
    fi
    dest_dir=$(mktemp -d)
    base_dest=$(basename $dest_dir)

    trap "rm -rf $dest_dir; docker rmi $base_dest/image" EXIT

    ELEMENTS_PATH=$DIB_ELEMENTS:$TEST_ELEMENTS \
        $DIB_CMD -x $type_arg --docker-target=$base_dest/image \
        -o $dest_dir/image -n fake-os

    format=$(echo $format | tr ',' ' ')
    for format in $format; do
        if [ $format != 'docker' ]; then
            img_path="$dest_dir/image.$format"
            if ! [ -f "$img_path" ]; then
                echo "Error: No image with name $img_path found!"
                exit 1
            else
                echo "Found image $img_path."
            fi
        else
            if ! docker images | grep $base_dest/image ; then
                echo "Error: No docker image with name $base_dest/image found!"
                exit 1
            else
                echo "Found docker image $base_dest/image"
            fi
        fi
    done

    trap EXIT
    rm -rf $dest_dir
    if docker images | grep $base_dest/image ; then
        docker rmi $base_dest/image
    fi
}

function run_disk_element_test() {
    test_element=$1
    element=$2

    dest_dir=$(mktemp -d)

    trap "rm -rf $dest_dir /tmp/dib-test-should-fail" EXIT

    if break="after-error" break_outside_target=1 \
        break_cmd="cp \$TMP_MOUNT_PATH/tmp/dib-test-should-fail /tmp/ 2>&1 > /dev/null || true" \
        ELEMENTS_PATH=$DIB_ELEMENTS:$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -t tar -o $dest_dir/image -n $element $test_element; then
        if ! [ -f "$dest_dir/image.tar" ]; then
            echo "Error: Build failed for element: $element, test-element: $test_element."
            echo "No image $dest_dir/image.tar found!"
            exit 1
        else
            if tar -t $dest_dir/image.tar | grep -q /tmp/dib-test-should-fail; then
                echo "Error: Element: $element, test-element $test_element should have failed, but passed."
                exit 1
            else
                echo "PASS: Element $element, test-element: $test_element"
            fi
        fi
    else
        if [ -f "/tmp/dib-test-should-fail" ]; then
            echo "PASS: Element $element, test-element: $test_element"
        else
            echo "Error: Build failed for element: $element, test-element: $test_element."
            exit 1
        fi
    fi

    trap EXIT
    rm -rf $dest_dir /tmp/dib-test-should-fail
}

function run_ramdisk_element_test() {
    test_element=$1
    element=$2

    dest_dir=$(mktemp -d)

    if ELEMENTS_PATH=$DIB_ELEMENTS/$element/test-elements \
        $DIB_CMD -o $dest_dir/image $element $test_element; then
        # TODO(dtantsur): test also kernel presence once we sort out its naming
        # problem (vmlinuz vs kernel)
        if ! [ -f "$dest_dir/image.initramfs" ]; then
            echo "Error: Build failed for element: $element, test-element: $test_element."
            echo "No image $dest_dir/image.initramfs found!"
            exit 1
        else
            echo "PASS: Element $element, test-element: $test_element"
        fi
    else
        echo "Error: Build failed for element: $element, test-element: $test_element."
        exit 1
    fi
}
