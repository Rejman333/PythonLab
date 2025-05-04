from pycluster.src.cli_parse import prepare_cli
from pycluster.src.img_procesing import ImgProcessor
from pycluster.src.save import save_to_img

def main():
    args = prepare_cli()
    print("I am working!")
    img_processor = ImgProcessor(args.filename)
    img_processor.create_clusters(args.gray, args.threshold)


    img_processor.plot_clusters_on_img(img_processor.img, img_processor.clusters)
    save_to_img(img_processor.img, img_processor.clusters, "data/results.jpg")

if __name__ == "__main__":
    main()
